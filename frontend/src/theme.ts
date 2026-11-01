import { createTheme } from "@mui/material";

const charcoal = "#272727";
const teal = "#56c4be";

const createAppTheme = (mode: "light" | "dark") =>
	createTheme({
		palette:
			mode === "dark"
				? {
						mode,
						primary: { main: teal },
						secondary: { main: charcoal },
						background: { default: "#1f1f1f", paper: charcoal },
						text: { primary: "#e6e6e6", secondary: "#bebebe" },
						success: { main: "#6dca70" },
					}
				: {
						mode,
						primary: { main: charcoal },
						secondary: { main: teal },
						background: { default: "#f5f5f5", paper: "#ffffff" },
						text: { primary: "#242424", secondary: "#a0a0a0" },
					},
		components: {
			MuiAppBar: {
				styleOverrides: {
					root:
						mode === "light"
							? {
									"&.main-header": {
										backgroundColor: charcoal,
										color: "#ffffff",
									},
								}
							: {},
				},
			},
		},
	});

export const lightTheme = createAppTheme("light");
export const darkTheme = createAppTheme("dark");
