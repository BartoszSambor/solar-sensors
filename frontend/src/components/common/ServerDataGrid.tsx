import { Alert, Box, Paper, type Theme, useMediaQuery } from "@mui/material";
import {
	DataGrid,
	type GridColDef,
	type GridFilterItem,
	type GridFilterModel,
	type GridPaginationModel,
	type GridSortModel,
	type GridValidRowModel,
} from "@mui/x-data-grid";
import { type ReactNode, useEffect, useMemo, useState } from "react";
import { useDebouncedValue } from "../../utils/debounce";
import { errorMessage } from "../../utils/useFetch";

export interface PageQuery {
	sortField?: string;
	sortDirection?: string;
	limit: number;
	skip: number;
	// Filter panel items that have a value (debounced).
	filters: GridFilterItem[];
}

interface ServerDataGridProps<R extends GridValidRowModel> {
	// Both should be module-level constants.
	columns: GridColDef<R>[];
	mobileFields: string[];
	defaultSortField: string;
	// Must be memoized; a new function triggers a refetch.
	fetchRows: (query: PageQuery) => Promise<{ rows: R[]; total: number }>;
	onRowClick?: (row: R) => void;
	filters?: ReactNode;
}

// Shared DataGrid with server-side pagination, sorting and filtering.
const ServerDataGrid = <R extends GridValidRowModel>({
	columns,
	mobileFields,
	defaultSortField,
	fetchRows,
	onRowClick,
	filters,
}: ServerDataGridProps<R>) => {
	const [rows, setRows] = useState<R[]>([]);
	const [rowCount, setRowCount] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
		page: 0,
		pageSize: 20,
	});
	const [sortModel, setSortModel] = useState<GridSortModel>([
		{ field: defaultSortField, sort: "asc" },
	]);
	const [filterModel, setFilterModel] = useState<GridFilterModel>({
		items: [],
	});
	// Only the filter panel (typed values) is debounced; paging and sorting fetch immediately.
	const debouncedFilterModel = useDebouncedValue(filterModel);
	const isMobile = useMediaQuery((theme: Theme) =>
		theme.breakpoints.down("sm"),
	);

	const visibleColumns = useMemo(
		() =>
			columns
				.filter((col) => !isMobile || mobileFields.includes(col.field))
				.map((col) => ({ hideable: false, ...col })),
		[columns, mobileFields, isMobile],
	);

	useEffect(() => {
		let active = true;
		const [sort] = sortModel;
		setLoading(true);
		setError(null);
		fetchRows({
			sortField: sort?.field,
			sortDirection: sort?.sort ?? undefined,
			limit: paginationModel.pageSize,
			skip: paginationModel.page * paginationModel.pageSize,
			filters: debouncedFilterModel.items.filter(
				(item) =>
					item.value ||
					item.operator === "isEmpty" ||
					item.operator === "isNotEmpty",
			),
		})
			.then(
				(result) => {
					if (!active) return;
					setRows(result.rows);
					setRowCount(result.total);
				},
				(err) => {
					if (!active) return;
					setError(errorMessage(err));
					setRows([]);
					setRowCount(0);
				},
			)
			.finally(() => active && setLoading(false));
		return () => {
			active = false;
		};
	}, [fetchRows, paginationModel, sortModel, debouncedFilterModel]);

	return (
		<Paper sx={{ width: "100%", mb: 2 }}>
			{filters && (
				<Box
					sx={{
						p: 2,
						display: "flex",
						flexWrap: "wrap",
						gap: 2,
						borderBottom: 1,
						borderColor: "divider",
					}}
				>
					{filters}
				</Box>
			)}
			{error && <Alert severity="error">{error}</Alert>}
			<DataGrid
				rows={rows}
				columns={visibleColumns}
				rowCount={rowCount}
				loading={loading}
				paginationMode="server"
				sortingMode="server"
				filterMode="server"
				paginationModel={paginationModel}
				onPaginationModelChange={setPaginationModel}
				sortModel={sortModel}
				onSortModelChange={setSortModel}
				filterModel={filterModel}
				onFilterModelChange={setFilterModel}
				pageSizeOptions={[10, 20, 50]}
				onRowClick={onRowClick && ((params) => onRowClick(params.row))}
				showToolbar
				slotProps={{ toolbar: { showQuickFilter: false } }}
				autoHeight
				disableColumnSelector
				disableRowSelectionOnClick
				sx={{
					border: "none",
					"& .MuiDataGrid-row": { cursor: onRowClick ? "pointer" : "default" },
					"& .MuiDataGrid-cell:focus": { outline: "none" },
				}}
			/>
		</Paper>
	);
};

export default ServerDataGrid;
