import { Alert, Box, Button, TextField, Typography } from "@mui/material";
import { type FormEvent, useState } from "react";
import { login } from "@/client";
import PageLayout from "../../components/common/PageLayout";
import { saveAccessToken } from "../../utils/auth";
import { errorMessage } from "../../utils/useFetch";

const LoginPage = () => {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [loading, setLoading] = useState(false);

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		setError(null);
		setLoading(true);
		try {
			const { data } = await login({ body: { username, password } });
			const { accessToken } = data;
			saveAccessToken(accessToken);
			// Full reload so every component picks up the new session.
			window.location.href = "/";
		} catch (err) {
			setError(
				errorMessage(
					err,
					"Login failed. Please check your username and password.",
				),
			);
		} finally {
			setLoading(false);
		}
	};

	return (
		<PageLayout maxWidth="xs">
			<Box
				component="form"
				onSubmit={handleSubmit}
				noValidate
				sx={{
					mt: 4,
					display: "flex",
					flexDirection: "column",
					alignItems: "center",
				}}
			>
				<Typography component="h1" variant="h5">
					Sign In
				</Typography>
				{error && (
					<Alert severity="error" sx={{ width: "100%", mt: 2 }}>
						{error}
					</Alert>
				)}
				<TextField
					margin="normal"
					required
					fullWidth
					id="username"
					label="Username"
					autoComplete="username"
					autoFocus
					value={username}
					onChange={(e) => setUsername(e.target.value)}
					error={!!error}
				/>
				<TextField
					margin="normal"
					required
					fullWidth
					id="password"
					label="Password"
					type="password"
					autoComplete="current-password"
					value={password}
					onChange={(e) => setPassword(e.target.value)}
					error={!!error}
				/>
				<Button
					type="submit"
					fullWidth
					variant="contained"
					sx={{ mt: 3, mb: 2 }}
					disabled={loading}
				>
					{loading ? "Signing In..." : "Sign In"}
				</Button>
			</Box>
		</PageLayout>
	);
};

export default LoginPage;
