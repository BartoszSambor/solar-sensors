import SearchIcon from "@mui/icons-material/Search";
import { InputAdornment, TextField } from "@mui/material";

interface SearchFieldProps {
	value: string;
	onChange: (value: string) => void;
	label?: string;
	placeholder?: string;
}

const SearchField = ({
	value,
	onChange,
	label,
	placeholder,
}: SearchFieldProps) => (
	<TextField
		size="small"
		label={label}
		placeholder={placeholder}
		value={value}
		onChange={(e) => onChange(e.target.value)}
		sx={{ width: 200 }}
		slotProps={{
			input: {
				startAdornment: (
					<InputAdornment position="start">
						<SearchIcon fontSize="small" />
					</InputAdornment>
				),
			},
		}}
	/>
);

export default SearchField;
