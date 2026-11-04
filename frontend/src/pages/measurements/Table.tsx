import { Alert, Box, Button, MenuItem, Paper, TextField } from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { type FormEvent, useState } from "react";
import {
	createMeasurement,
	type ListMeasurementsData,
	listMeasurements,
	type MeasurementRead,
} from "@/client";
import PageLayout from "../../components/common/PageLayout";
import { errorMessage, useFetch } from "../../utils/useFetch";

type Query = NonNullable<ListMeasurementsData["query"]>;

// <input type="datetime-local"> gives local time without a zone; the API wants ISO.
const toIso = (local: string) =>
	local ? new Date(local).toISOString() : undefined;

const columns: GridColDef<MeasurementRead>[] = [
	{ field: "id", headerName: "ID", width: 90 },
	{ field: "seriesId", headerName: "Series", width: 100 },
	{ field: "sensorId", headerName: "Sensor", width: 100 },
	{ field: "value", headerName: "Value", width: 120 },
	{
		field: "timestamp",
		headerName: "Timestamp",
		flex: 1,
		minWidth: 200,
		valueFormatter: (value: string) => new Date(value).toLocaleString(),
	},
];

const MeasurementsTablePage = () => {
	// Filter form state, applied to `query` on submit.
	const [series, setSeries] = useState("");
	const [from, setFrom] = useState("");
	const [to, setTo] = useState("");
	const [sort, setSort] = useState<Query["sort"]>("-timestamp");
	const [limit, setLimit] = useState(100);
	const [query, setQuery] = useState<Query>({ sort, limit });

	// New measurement form state.
	const [sensorId, setSensorId] = useState("");
	const [value, setValue] = useState("");
	const [timestamp, setTimestamp] = useState("");
	const [actionError, setActionError] = useState<string>();
	const [reloadKey, setReloadKey] = useState(0);

	const { data, loading, error } = useFetch(
		async () => (await listMeasurements({ query })).data,
		`${JSON.stringify(query)}-${reloadKey}`,
	);

	const onFilter = (e: FormEvent) => {
		e.preventDefault();
		setQuery({
			series: series.replace(/\s/g, "") || undefined,
			from: toIso(from),
			to: toIso(to),
			sort,
			limit,
		});
	};

	const onCreate = async (e: FormEvent) => {
		e.preventDefault();
		setActionError(undefined);
		try {
			await createMeasurement({
				query: { sensorId: Number(sensorId) },
				body: {
					value: Number(value),
					timestamp: toIso(timestamp) ?? new Date().toISOString(),
				},
			});
			setValue("");
			setReloadKey((key) => key + 1);
		} catch (err) {
			setActionError(errorMessage(err));
		}
	};

	return (
		<PageLayout error={error}>
			<Paper
				component="form"
				onSubmit={onCreate}
				sx={{ p: 2, mb: 2, display: "flex", gap: 2, flexWrap: "wrap" }}
			>
				<TextField
					label="Sensor ID"
					type="number"
					size="small"
					required
					value={sensorId}
					onChange={(e) => setSensorId(e.target.value)}
				/>
				<TextField
					label="Value"
					type="number"
					size="small"
					required
					slotProps={{ htmlInput: { step: "any" } }}
					value={value}
					onChange={(e) => setValue(e.target.value)}
				/>
				<TextField
					label="Timestamp (default: now)"
					type="datetime-local"
					size="small"
					slotProps={{ inputLabel: { shrink: true } }}
					value={timestamp}
					onChange={(e) => setTimestamp(e.target.value)}
				/>
				<Button type="submit" variant="contained">
					Add Measurement
				</Button>
			</Paper>
			{actionError && (
				<Alert severity="error" sx={{ mb: 2 }}>
					{actionError}
				</Alert>
			)}
			<Paper
				component="form"
				onSubmit={onFilter}
				sx={{ p: 2, mb: 2, display: "flex", gap: 2, flexWrap: "wrap" }}
			>
				<TextField
					label="Series IDs"
					placeholder="e.g. 1,2"
					size="small"
					value={series}
					onChange={(e) => setSeries(e.target.value)}
				/>
				<TextField
					label="From"
					type="datetime-local"
					size="small"
					slotProps={{ inputLabel: { shrink: true } }}
					value={from}
					onChange={(e) => setFrom(e.target.value)}
				/>
				<TextField
					label="To"
					type="datetime-local"
					size="small"
					slotProps={{ inputLabel: { shrink: true } }}
					value={to}
					onChange={(e) => setTo(e.target.value)}
				/>
				<TextField
					select
					label="Sort"
					size="small"
					value={sort}
					onChange={(e) => setSort(e.target.value as Query["sort"])}
				>
					<MenuItem value="-timestamp">Newest first</MenuItem>
					<MenuItem value="timestamp">Oldest first</MenuItem>
				</TextField>
				<TextField
					label="Limit"
					type="number"
					size="small"
					slotProps={{ htmlInput: { min: 1, max: 10000 } }}
					value={limit}
					onChange={(e) => setLimit(Number(e.target.value))}
				/>
				<Button type="submit" variant="outlined">
					Apply
				</Button>
			</Paper>
			<Box sx={{ height: 500 }}>
				<DataGrid
					rows={data ?? []}
					columns={columns}
					// Only the first load shows the overlay; reloads keep the old rows.
					loading={loading && !data}
					disableRowSelectionOnClick
				/>
			</Box>
		</PageLayout>
	);
};

export default MeasurementsTablePage;
