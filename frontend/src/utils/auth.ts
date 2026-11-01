const ACCESS_TOKEN_KEY = "access_token";

export function saveAccessToken(accessToken: string) {
	localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
}

export function getAccessToken(): string {
	return localStorage.getItem(ACCESS_TOKEN_KEY) || "";
}

export function clearAuthData() {
	localStorage.removeItem(ACCESS_TOKEN_KEY);
}

export function isLoggedIn(): boolean {
	return !!getAccessToken();
}
