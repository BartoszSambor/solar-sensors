import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { client } from "./client/client.gen";
import { clearAuthData, getAccessToken, isLoggedIn } from "./utils/auth";

client.setConfig({ auth: () => getAccessToken() });

// A 401 while signed in means the token expired or was revoked: sign in again.
client.instance.interceptors.response.use(undefined, (error) => {
	if (error.response?.status === 401 && isLoggedIn()) {
		clearAuthData();
		window.location.assign("/login");
	}
	return Promise.reject(error);
});

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
	<React.StrictMode>
		<BrowserRouter>
			<App />
		</BrowserRouter>
	</React.StrictMode>,
);
