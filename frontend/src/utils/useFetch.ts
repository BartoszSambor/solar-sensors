import { useEffect, useState } from "react";

export const errorMessage = (
	err: unknown,
	fallback = "Request failed.",
): string => {
	// AxiosError: FastAPI puts the reason in the response body's "detail".
	const detail = (err as any)?.response?.data?.detail;
	return typeof detail === "string" && detail
		? detail
		: (err as Error)?.message || fallback;
};

interface FetchState<T> {
	data?: T;
	loading: boolean;
	error?: string;
}

// Runs `load` on mount and whenever `key` changes.
export const useFetch = <T>(load: () => Promise<T>, key?: unknown) => {
	const [state, setState] = useState<FetchState<T>>({ loading: true });

	// biome-ignore lint/correctness/useExhaustiveDependencies: refetch only when key changes
	useEffect(() => {
		let active = true;
		// Keep the previous data while refetching so the view doesn't flash empty.
		setState((prev) => ({ data: prev.data, loading: true }));
		load().then(
			(data) => active && setState({ data, loading: false }),
			(err) => active && setState({ loading: false, error: errorMessage(err) }),
		);
		return () => {
			active = false;
		};
	}, [key]);

	return state;
};
