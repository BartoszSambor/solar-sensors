import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import {
	Alert,
	Box,
	Button,
	IconButton,
	Paper,
	TextField,
} from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { type FormEvent, useState } from "react";
import {
	createSeries,
	deleteSeries,
	listSeries,
	type SeriesRead,
	updateSeries,
} from "@/client";
import PageLayout from "../../components/common/PageLayout";
import { isLoggedIn } from "../../utils/auth";
import { errorMessage, useFetch } from "../../utils/useFetch";

// Numbers are kept as strings so the inputs can be cleared or hold "-".
const emptyForm = {
	name: "",
	minValue: "",
	maxValue: "",
	unit: "",
	color: "#1f77b4",
	icon: "",
};

const SeriesTablePage = () => {
	const [reloadKey, setReloadKey] = useState(0);
	// Anonymous users can browse; only signed-in users can change data.
	const canEdit = isLoggedIn();
	const [form, setForm] = useState(emptyForm);
	const [editedId, setEditedId] = useState<number>();
	const [actionError, setActionError] = useState<string>();
	const { data, loading, error } = useFetch(
		async () => (await listSeries()).data,
		reloadKey,
	);
	const reload = () => setReloadKey((key) => key + 1);

	const field = (name: keyof typeof emptyForm) => ({
		value: form[name],
		onChange: (e: { target: { value: string } }) =>
			setForm({ ...form, [name]: e.target.value }),
	});

	const resetForm = () => {
		setForm(emptyForm);
		setEditedId(undefined);
	};

	const onSubmit = async (e: FormEvent) => {
		e.preventDefault();
		setActionError(undefined);
		const body = {
			...form,
			minValue: Number(form.minValue),
			maxValue: Number(form.maxValue),
		};
		try {
			if (editedId === undefined) {
				await createSeries({ body });
			} else {
				await updateSeries({ path: { series_id: editedId }, body });
			}
			resetForm();
			reload();
		} catch (err) {
			setActionError(errorMessage(err));
		}
	};

	const onEdit = (series: SeriesRead) => {
		setActionError(undefined);
		setEditedId(series.id);
		setForm({
			name: series.name,
			minValue: String(series.minValue),
			maxValue: String(series.maxValue),
			unit: series.unit,
			color: series.color,
			icon: series.icon,
		});
	};

	const onDelete = async (series: SeriesRead) => {
		const confirmed = window.confirm(
			`Delete series "${series.name}"? All its sensors and measurements will be deleted too.`,
		);
		if (!confirmed) return;
		setActionError(undefined);
		try {
			await deleteSeries({ path: { series_id: series.id } });
			if (editedId === series.id) resetForm();
			reload();
		} catch (err) {
			setActionError(errorMessage(err));
		}
	};

	const columns: GridColDef<SeriesRead>[] = [
		{ field: "id", headerName: "ID", width: 80 },
		{
			field: "color",
			headerName: "Color",
			width: 80,
			renderCell: ({ value }) => (
				<Box
					sx={{
						mt: 1.5,
						width: 24,
						height: 24,
						borderRadius: 1,
						bgcolor: value,
					}}
				/>
			),
		},
		{ field: "name", headerName: "Name", flex: 1, minWidth: 150 },
		{ field: "unit", headerName: "Unit", width: 90 },
		{ field: "minValue", headerName: "Min", width: 100 },
		{ field: "maxValue", headerName: "Max", width: 100 },
		{ field: "icon", headerName: "Icon", width: 130 },
		{
			field: "actions",
			headerName: "",
			width: 110,
			sortable: false,
			filterable: false,
			renderCell: ({ row }) => (
				<>
					<IconButton
						aria-label={`edit ${row.name}`}
						onClick={() => onEdit(row)}
					>
						<EditIcon />
					</IconButton>
					<IconButton
						aria-label={`delete ${row.name}`}
						onClick={() => onDelete(row)}
					>
						<DeleteIcon />
					</IconButton>
				</>
			),
		},
	];

	return (
		<PageLayout error={error}>
			{canEdit && (
				<Paper
					component="form"
					onSubmit={onSubmit}
					sx={{ p: 2, mb: 2, display: "flex", gap: 2, flexWrap: "wrap" }}
				>
					<TextField label="Name" size="small" required {...field("name")} />
					<TextField
						label="Min value"
						type="number"
						size="small"
						required
						slotProps={{ htmlInput: { step: "any" } }}
						{...field("minValue")}
					/>
					<TextField
						label="Max value"
						type="number"
						size="small"
						required
						slotProps={{ htmlInput: { step: "any" } }}
						{...field("maxValue")}
					/>
					<TextField label="Unit" size="small" required {...field("unit")} />
					<TextField
						label="Color"
						type="color"
						size="small"
						sx={{ width: 90 }}
						{...field("color")}
					/>
					<TextField label="Icon" size="small" required {...field("icon")} />
					<Button type="submit" variant="contained">
						{editedId === undefined ? "Add Series" : "Save"}
					</Button>
					{editedId !== undefined && (
						<Button onClick={resetForm}>Cancel</Button>
					)}
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
		</PageLayout>
	);
};

export default SeriesTablePage;
