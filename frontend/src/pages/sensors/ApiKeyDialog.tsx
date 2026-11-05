import {
	Alert,
	Button,
	Dialog,
	DialogActions,
	DialogContent,
	DialogTitle,
	TextField,
} from "@mui/material";
import { useState } from "react";
import type { SensorCreated } from "@/client";

interface ApiKeyDialogProps {
	sensor?: SensorCreated;
	onClose: () => void;
}

// Shows a new sensor's API key. The backend never returns it again.
const ApiKeyDialog = ({ sensor, onClose }: ApiKeyDialogProps) => {
	const [copied, setCopied] = useState(false);

	const onCopy = async () => {
		if (!sensor) return;
		// The clipboard API only works on HTTPS or localhost; the field stays
		// selectable for copying by hand.
		try {
			await navigator.clipboard.writeText(sensor.apiKey);
			setCopied(true);
		} catch {
			setCopied(false);
		}
	};

	const close = () => {
		setCopied(false);
		onClose();
	};

	return (
		// No onClose: a stray click or Esc must not lose the key.
		<Dialog open={Boolean(sensor)} maxWidth="sm" fullWidth>
			<DialogTitle>API key for "{sensor?.name}"</DialogTitle>
			<DialogContent>
				<Alert severity="warning" sx={{ mb: 2 }}>
					Copy the key now and store it on the sensor. It is shown only once and
					can't be recovered; a lost key means adding the sensor again.
				</Alert>
				<TextField
					fullWidth
					value={sensor?.apiKey ?? ""}
					slotProps={{ htmlInput: { readOnly: true } }}
					onFocus={(e) => e.target.select()}
				/>
			</DialogContent>
			<DialogActions>
				<Button onClick={onCopy}>{copied ? "Copied" : "Copy"}</Button>
				<Button variant="contained" onClick={close}>
					I've saved it
				</Button>
			</DialogActions>
		</Dialog>
	);
};

export default ApiKeyDialog;
