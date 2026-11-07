import DeleteIcon from "@mui/icons-material/Delete";
import {
	Alert,
	Box,
	Button,
	IconButton,
	MenuItem,
	Paper,
	TextField,
} from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { type FormEvent, useState } from "react";
import {
	createSensor,
	deleteSensor,
	listSensors,
	listSeries,
	type SensorCreated,
	type SensorRead,
} from "@/client";
import PageLayout from "../../components/common/PageLayout";
import { isLoggedIn } from "../../utils/auth";
import { seriesLabel } from "../../utils/series";
import { errorMessage, useFetch } from "../../utils/useFetch";
import ApiKeyDialog from "./ApiKeyDialog";

const SensorsTablePage = () => {
	const [reloadKey, setReloadKey] = useState(0);
	// The page is only reachable when signed in (sensors are admin-only).
	const canEdit = isLoggedIn();
	const [name, setName] = useState("");
	const [seriesId, setSeriesId] = useState("");
	const [actionError, setActionError] = useState<string>();
	const [created, setCreated] = useState<SensorCreated>();
	const { data, loading, error } = useFetch(
		async () => (await listSensors()).data,
		reloadKey,
	);
	const { data: seriesList } = useFetch(async () => (await listSeries()).data);
	const reload = () => setReloadKey((key) => key + 1);
	const seriesName = (id: number) =>
		seriesList?.find((series) => series.id === id)?.name ?? id;

	const onCreate = async (e: FormEvent) => {
		e.preventDefault();
		setActionError(undefined);
		try {
			const { data } = await createSensor({
				body: { name, seriesId: Number(seriesId) },
			});
			setCreated(data);
			setName("");
			setSeriesId("");
			reload();
		} catch (err) {
			setActionError(errorMessage(err));
		}
	};

	const onDelete = async (sensorId: number) => {
		setActionError(undefined);
		try {
			await deleteSensor({ path: { sensor_id: sensorId } });
			reload();
		} catch (err) {
			setActionError(errorMessage(err));
		}
	};

	const columns: GridColDef<SensorRead>[] = [
		{ field: "id", headerName: "ID", width: 90 },
		{ field: "name", headerName: "Name", flex: 1, minWidth: 150 },
		{
			field: "seriesId",
			headerName: "Series",
			flex: 1,
			minWidth: 150,
			valueFormatter: (value: number) => seriesName(value),
		},
		{
			field: "actions",
			headerName: "",
			width: 70,
			sortable: false,
			filterable: false,
			renderCell: ({ row }) => (
				<IconButton
					aria-label={`delete ${row.name}`}
					onClick={() => onDelete(row.id)}
				>
					<DeleteIcon />
				</IconButton>
			),
		},
	];

	return (
		<PageLayout error={error}>
			{canEdit && (
				<Paper
					component="form"
					onSubmit={onCreate}
					sx={{ p: 2, mb: 2, display: "flex", gap: 2, flexWrap: "wrap" }}
				>
					<TextField
						label="Name"
						size="small"
						required
						value={name}
						onChange={(e) => setName(e.target.value)}
					/>
					<TextField
						select
						label="Series"
						size="small"
						required
						sx={{ minWidth: 180 }}
						value={seriesId}
						onChange={(e) => setSeriesId(e.target.value)}
					>
						{(seriesList ?? []).map((series) => (
							<MenuItem key={series.id} value={series.id}>
								{seriesLabel(series)}
							</MenuItem>
						))}
					</TextField>
					<Button type="submit" variant="contained">
						Add Sensor
					</Button>
				</Paper>
			)}
			{actionError && (
				<Alert severity="error" sx={{ mb: 2 }}>
					{actionError}
				</Alert>
			)}
			<Box sx={{ height: 500 }}>
				<DataGrid
					rows={data ?? []}
					columns={
						canEdit ? columns : columns.filter((c) => c.field !== "actions")
					}
					// Only the first load shows the overlay; reloads keep the old rows.
					loading={loading && !data}
					disableRowSelectionOnClick
				/>
			</Box>
			<ApiKeyDialog sensor={created} onClose={() => setCreated(undefined)} />
		</PageLayout>
	);
};

export default SensorsTablePage;
