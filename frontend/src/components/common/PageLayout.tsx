import { Alert, type Breakpoint, Container } from "@mui/material";
import type { ReactNode } from "react";
import Header from "./Header";

interface PageLayoutProps {
	children?: ReactNode;
	maxWidth?: Breakpoint;
	error?: string | null;
}

const PageLayout = ({ children, maxWidth = "lg", error }: PageLayoutProps) => (
	<>
		<Header />
		<Container component="main" maxWidth={maxWidth} sx={{ mt: 4, mb: 4 }}>
			{error ? <Alert severity="error">{error}</Alert> : children}
		</Container>
	</>
);

export default PageLayout;
