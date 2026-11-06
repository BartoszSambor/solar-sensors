import {
	Alert,
	Box,
	Button,
	LinearProgress,
	Paper,
	TextField,
	Typography,
} from "@mui/material";
import axios from "axios";
import { type FormEvent, useEffect, useState } from "react";
import PageLayout from "../../components/common/PageLayout";
import { errorMessage } from "../../utils/useFetch";

// The simulator is a separate service (simulator/); nginx routes /simulator/ to it.
interface RunStatus {
	running: boolean;
	total: number;
	sent: number;
	failed: number;
	lastError: string | null;
	apiUrls: string[];
}

const RUN_URL = "/simulator/api/run";

const SimulatorPage = () => {
	// Bumped to re-read the status (after start and stop).
	const [refresh, setRefresh] = useState(0);
	const [status, setStatus] = useState<RunStatus>();
	const [connectError, setConnectError] = useState<string>();
	const [actionError, setActionError] = useState<string>();

	const [apiUrl, setApiUrl] = useState("");
	// Kept in memory only; a real sensor stores its own key.
	const [apiKey, setApiKey] = useState("");
	const [count, setCount] = useState("100");
	const [minValue, setMinValue] = useState("0");
	const [maxValue, setMaxValue] = useState("100");

	// biome-ignore lint/correctness/useExhaustiveDependencies: refresh is a trigger
	useEffect(() => {
		let active = true;
		let timer: number | undefined;
		const poll = async () => {
			try {
				const { data } = await axios.get<RunStatus>(RUN_URL);
				if (!active) return;
				setStatus(data);
				setConnectError(undefined);
				setApiUrl((url) => url || data.apiUrls[0] || window.location.origin);
				// Poll while a run is in progress.
				if (data.running) timer = window.setTimeout(poll, 1000);
			} catch (err) {
				if (active) setConnectError(errorMessage(err));
			}
		};
		poll();
		return () => {
			active = false;
			window.clearTimeout(timer);
		};
	}, [refresh]);

	const onStart = async (e: FormEvent) => {
		e.preventDefault();
		setActionError(undefined);
		try {
			await axios.post(RUN_URL, {
				apiUrl,
				apiKey,
				count: Number(count),
				minValue: Number(minValue),
				maxValue: Number(maxValue),
			});
			setRefresh((r) => r + 1);
		} catch (err) {
			setActionError(errorMessage(err));
		}
	};

	const onStop = async () => {
		setActionError(undefined);
		try {
			await axios.delete(RUN_URL);
			setRefresh((r) => r + 1);
		} catch (err) {
			setActionError(errorMessage(err));
		}
	};

	const done = status ? status.sent + status.failed : 0;

	return (
		<PageLayout>
			<Typography variant="h5" sx={{ mb: 1 }}>
				Sensor simulator
			</Typography>
			<Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
				A separate service that acts as an IoT device: it sends measurements to
				the API over HTTPS using a sensor's API key.
			</Typography>

			{connectError && (
				<Alert severity="error" sx={{ mb: 2 }}>
					Simulator not reachable: {connectError}
				</Alert>
			)}

			<Paper
				component="form"
				onSubmit={onStart}
				sx={{ p: 2, mb: 2, display: "flex", gap: 2, flexWrap: "wrap" }}
			>
				<TextField
					label="API URL"
					size="small"
					required
					sx={{ minWidth: 280 }}
					value={apiUrl}
					onChange={(e) => setApiUrl(e.target.value)}
					helperText={
						status?.apiUrls.length
							? `Allowed: ${status.apiUrls.join(", ")}`
							: undefined
					}
				/>
				<TextField
					label="Sensor API key"
					type="password"
					size="small"
					required
					autoComplete="off"
					sx={{ minWidth: 280 }}
					value={apiKey}
					onChange={(e) => setApiKey(e.target.value)}
				/>
				<TextField
					label="Number of results"
					type="number"
					size="small"
					required
					slotProps={{ htmlInput: { min: 1, max: 10000 } }}
					value={count}
					onChange={(e) => setCount(e.target.value)}
				/>
				<TextField
					label="Min value"
					type="number"
					size="small"
					required
					slotProps={{ htmlInput: { step: "any" } }}
					value={minValue}
					onChange={(e) => setMinValue(e.target.value)}
				/>
				<TextField
					label="Max value"
					type="number"
					size="small"
					required
					slotProps={{ htmlInput: { step: "any" } }}
					value={maxValue}
					onChange={(e) => setMaxValue(e.target.value)}
				/>
				<Box sx={{ display: "flex", gap: 1 }}>
					<Button
						type="submit"
						variant="contained"
						disabled={!status || status.running}
					>
						Start
					</Button>
					<Button
						variant="outlined"
						color="error"
						disabled={!status?.running}
						onClick={onStop}
					>
						Stop
					</Button>
				</Box>
			</Paper>

			{actionError && (
				<Alert severity="error" sx={{ mb: 2 }}>
					{actionError}
				</Alert>
			)}

			{status && status.total > 0 && (
				<Paper sx={{ p: 2 }}>
					<Typography sx={{ mb: 1 }}>
						{status.running
							? "Running"
							: done < status.total
								? "Stopped"
								: "Finished"}
						: sent {status.sent} of {status.total}, failed {status.failed}
					</Typography>
					<LinearProgress
						variant="determinate"
						value={(done / status.total) * 100}
					/>
					{status.lastError && (
						<Alert severity="warning" sx={{ mt: 2 }}>
							Last error: {status.lastError}
						</Alert>
					)}
				</Paper>
			)}
		</PageLayout>
	);
};

export default SimulatorPage;
