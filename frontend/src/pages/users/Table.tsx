import { Avatar } from "@mui/material";
import type { GridColDef } from "@mui/x-data-grid";
import { useCallback, useState } from "react";
import { type ListUsersData, listUsers, type UserRead } from "@/client";
import PageLayout from "../../components/common/PageLayout";
import SearchField from "../../components/common/SearchField";
import ServerDataGrid, {
	type PageQuery,
} from "../../components/common/ServerDataGrid";
import { useDebouncedValue } from "../../utils/debounce";
import { formatDate } from "../../utils/locale";

const columns: GridColDef<UserRead>[] = [
	{
		field: "avatar",
		headerName: "",
		width: 60,
		sortable: false,
		filterable: false,
		renderCell: ({ row }) => (
			<Avatar
				alt={row.username}
				sx={{ width: 32, height: 32, bgcolor: "primary.main" }}
			>
				{row.username.charAt(0).toUpperCase()}
			</Avatar>
		),
	},
	{ field: "username", headerName: "Username", flex: 1, minWidth: 150 },
	{
		field: "created_at",
		headerName: "Joined",
		type: "date",
		width: 180,
		valueFormatter: (value?: string) => formatDate(value, { fallback: "N/A" }),
	},
];

const mobileFields = ["avatar", "username"];

const UsersTablePage = () => {
	const [search, setSearch] = useState("");
	const debouncedSearch = useDebouncedValue(search);

	const fetchRows = useCallback(
		async ({ filters, ...query }: PageQuery) => {
			const params: NonNullable<ListUsersData["query"]> = {
				skip: query.skip,
				limit: query.limit,
				sort_field: query.sortField,
				sort_direction: query.sortDirection,
				username: debouncedSearch || undefined,
			};
			// Filter panel values override the search box.
			for (const { field, operator, value: raw } of filters) {
				const value = raw instanceof Date ? raw.toISOString() : raw;
				if (field === "username") params.username = value;
				else if (field === "created_at") {
					if (operator === "after" || operator === "onOrAfter")
						params.created_at_from = value;
					if (operator === "before" || operator === "onOrBefore")
						params.created_at_to = value;
				}
			}
			const { data } = await listUsers({ query: params });
			const { users, total } = data;
			return { rows: users, total };
		},
		[debouncedSearch],
	);

	return (
		<PageLayout>
			<ServerDataGrid
				columns={columns}
				mobileFields={mobileFields}
				defaultSortField="username"
				fetchRows={fetchRows}
				filters={
					<SearchField
						placeholder="Search users..."
						value={search}
						onChange={setSearch}
					/>
				}
			/>
		</PageLayout>
	);
};

export default UsersTablePage;
