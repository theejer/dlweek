import { View, Text } from "react-native";
import { Picker } from "@react-native-picker/picker";
import { TextInput } from "@/shared/components/TextInput";
import { Button } from "@/shared/components/Button";
import type { Location } from "@/features/trips/types";

type LocationEditorProps = {
  location: Location;
  onChange: (next: Location) => void;
  onRemove: () => void;
};

export function LocationEditor({ location, onChange, onRemove }: LocationEditorProps) {
  // Edits one location row for itinerary day.
  return (
    <View style={{ gap: 6, borderWidth: 1, borderColor: "#ddd", borderRadius: 8, padding: 8 }}>
      <Text style={{ fontSize: 12, color: "#6b7280", fontWeight: "600" }}>Location Name</Text>
      <TextInput
        placeholder="Location name"
        value={location.name}
        onChangeText={(value) => onChange({ ...location, name: value })}
      />
      <Text style={{ fontSize: 12, color: "#6b7280", fontWeight: "600" }}>District (Bihar)</Text>
      <TextInput
        placeholder="District (Bihar)"
        value={location.district ?? ""}
        onChangeText={(value) => onChange({ ...location, district: value || undefined })}
      />
      <Text style={{ fontSize: 12, color: "#6b7280", fontWeight: "600" }}>Block</Text>
      <TextInput
        placeholder="Block"
        value={location.block ?? ""}
        onChangeText={(value) => onChange({ ...location, block: value || undefined })}
      />
      <Text style={{ fontSize: 12, color: "#6b7280", fontWeight: "600" }}>Connectivity Zone</Text>
      <View style={{ borderWidth: 1, borderColor: "#d1d5db", borderRadius: 8, backgroundColor: "#ffffff" }}>
        <Picker
          selectedValue={location.connectivityZone ?? ""}
          onValueChange={(value: "" | "low" | "moderate" | "high" | "severe") => {
            onChange({
              ...location,
              connectivityZone: value || undefined,
            });
          }}
          style={{ color: "#111827" }}
        >
          <Picker.Item label="Select connectivity zone" value="" color="#9ca3af" />
          <Picker.Item label="Low" value="low" />
          <Picker.Item label="Moderate" value="moderate" />
          <Picker.Item label="High" value="high" />
          <Picker.Item label="Severe" value="severe" />
        </Picker>
      </View>
      <Button onPress={onRemove}>Remove location</Button>
      <Text style={{ fontSize: 12 }}>Use Bihar district/block names when known.</Text>
    </View>
  );
}
