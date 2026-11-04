import { CssBaseline, ThemeProvider, useMediaQuery } from "@mui/material";
import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/auth/login";
import MeasurementsTablePage from "./pages/measurements/Table";
import SensorsTablePage from "./pages/sensors/Table";
import SeriesTablePage from "./pages/series/Table";
import UsersTablePage from "./pages/users/Table";
import { darkTheme, lightTheme } from "./theme";

function App() {
	const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");

	return (
		<ThemeProvider theme={prefersDarkMode ? darkTheme : lightTheme}>
			<CssBaseline />
			<Routes>
				<Route path="/" element={<Navigate to="/sensors" replace />} />
				<Route path="/login" element={<LoginPage />} />
				<Route path="/series" element={<SeriesTablePage />} />
				<Route path="/sensors" element={<SensorsTablePage />} />
				<Route path="/measurements" element={<MeasurementsTablePage />} />
				<Route path="/users" element={<UsersTablePage />} />
			</Routes>
		</ThemeProvider>
	);
}

export default App;
