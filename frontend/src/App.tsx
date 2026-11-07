import { CssBaseline, ThemeProvider, useMediaQuery } from "@mui/material";
import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/auth/login";
import MeasurementsTablePage from "./pages/measurements/Table";
import SensorsTablePage from "./pages/sensors/Table";
import SeriesTablePage from "./pages/series/Table";
import SimulatorPage from "./pages/simulator/Simulator";
import UsersTablePage from "./pages/users/Table";
import { darkTheme, lightTheme } from "./theme";
import { isLoggedIn } from "./utils/auth";

function App() {
	const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");

	return (
		<ThemeProvider theme={prefersDarkMode ? darkTheme : lightTheme}>
			<CssBaseline />
			<Routes>
				<Route path="/" element={<Navigate to="/measurements" replace />} />
				<Route path="/login" element={<LoginPage />} />
				<Route path="/series" element={<SeriesTablePage />} />
				<Route
					path="/sensors"
					element={
						isLoggedIn() ? (
							<SensorsTablePage />
						) : (
							<Navigate to="/login" replace />
						)
					}
				/>
				<Route path="/measurements" element={<MeasurementsTablePage />} />
				<Route
					path="/simulator"
					element={
						isLoggedIn() ? <SimulatorPage /> : <Navigate to="/login" replace />
					}
				/>
				<Route
					path="/users"
					element={
						isLoggedIn() ? <UsersTablePage /> : <Navigate to="/login" replace />
					}
				/>
			</Routes>
		</ThemeProvider>
	);
}

export default App;
