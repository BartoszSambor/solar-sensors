export const formatDate = (
	dateString?: string | null,
	{ fallback = "" }: { fallback?: string } = {},
): string => {
	const date = new Date(dateString ?? "");
	if (!dateString || Number.isNaN(date.getTime())) return fallback;
	return date.toLocaleDateString("en-US", {
		day: "numeric",
		month: "long",
		year: "numeric",
	});
};
