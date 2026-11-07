import MenuIcon from "@mui/icons-material/Menu";
import {
	AppBar,
	Box,
	Button,
	Container,
	IconButton,
	Menu,
	MenuItem,
	Toolbar,
	Typography,
} from "@mui/material";
import { useState } from "react";
import { Link as RouterLink, useLocation, useNavigate } from "react-router-dom";
import { logout } from "@/client";
import { clearAuthData, isLoggedIn } from "../../utils/auth";

const Header = () => {
	const navigate = useNavigate();
	const { pathname } = useLocation();
	const [menuAnchorEl, setMenuAnchorEl] = useState<HTMLElement | null>(null);
	const isAuthenticated = isLoggedIn();

	const onLogout = () => {
		setMenuAnchorEl(null);
		// Best effort: the session is cleared locally even if the call fails.
		logout().catch(() => {});
		clearAuthData();
		navigate("/login");
	};

	const sections = [
		{ to: "/series", label: "Series" },
		{ to: "/measurements", label: "Measurements" },
		...(isAuthenticated
			? [
					{ to: "/sensors", label: "Sensors" },
					{ to: "/simulator", label: "Simulator" },
					{ to: "/users", label: "Users" },
				]
			: []),
	];

	return (
		<AppBar position="static" className="main-header" color="default">
			<Container maxWidth="lg">
				<Toolbar disableGutters>
					<Box
						component={RouterLink}
						to="/"
						sx={{
							display: "flex",
							alignItems: "center",
							textDecoration: "none",
							color: "inherit",
						}}
					>
						<Box
							component="img"
							src="/assets/images/logo.png"
							alt="Solar Sensors Logo"
							sx={{ height: 40, mr: 1 }}
						/>
						<Typography variant="h6" component="div">
							Solar Sensors
						</Typography>
					</Box>

					<Box
						component="nav"
						sx={{
							display: { xs: "none", md: "flex" },
							gap: 2,
							flexGrow: 1,
							ml: 2,
						}}
					>
						{sections.map(({ to, label }) => (
							<Button
								key={to}
								color="inherit"
								component={RouterLink}
								to={to}
								sx={{ fontWeight: pathname.startsWith(to) ? "bold" : "normal" }}
							>
								{label}
							</Button>
						))}
					</Box>

					<Box
						sx={{
							display: { xs: "none", md: "flex" },
							alignItems: "center",
							gap: 1,
						}}
					>
						{isAuthenticated ? (
							<Button variant="contained" color="secondary" onClick={onLogout}>
								Sign Out
							</Button>
						) : (
							<Button
								component={RouterLink}
								to="/login"
								variant="contained"
								color="secondary"
								size="small"
							>
								Sign In
							</Button>
						)}
					</Box>

					<Box sx={{ display: { xs: "flex", md: "none" }, ml: "auto" }}>
						<IconButton
							color="inherit"
							aria-label="open navigation menu"
							onClick={(e) => setMenuAnchorEl(e.currentTarget)}
						>
							<MenuIcon />
						</IconButton>
						<Menu
							anchorEl={menuAnchorEl}
							open={Boolean(menuAnchorEl)}
							onClose={() => setMenuAnchorEl(null)}
							anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
							transformOrigin={{ vertical: "top", horizontal: "right" }}
							keepMounted
						>
							{sections.map(({ to, label }) => (
								<MenuItem
									key={to}
									component={RouterLink}
									to={to}
									onClick={() => setMenuAnchorEl(null)}
								>
									{label}
								</MenuItem>
							))}
							{isAuthenticated ? (
								<MenuItem onClick={onLogout}>Sign Out</MenuItem>
							) : (
								<MenuItem
									component={RouterLink}
									to="/login"
									onClick={() => setMenuAnchorEl(null)}
								>
									Sign In
								</MenuItem>
							)}
						</Menu>
					</Box>
				</Toolbar>
			</Container>
		</AppBar>
	);
};

export default Header;
