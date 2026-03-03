import { TextInput as RNTextInput, type TextInputProps } from "react-native";

export function TextInput(props: TextInputProps) {
  return (
    <RNTextInput
      {...props}
      placeholderTextColor={props.placeholderTextColor ?? "#9ca3af"}
      style={[
        {
          borderWidth: 1,
          borderColor: "#ccc",
          padding: 10,
          borderRadius: 8,
          color: "#111827",
          backgroundColor: "#ffffff",
        },
        props.style,
      ]}
    />
  );
}
