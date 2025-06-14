import { Stack } from "./lib/stacks";
import { CodeGenerationModel } from "./lib/models";

export enum EditorTheme {
  ESPRESSO = "espresso",
  COBALT = "cobalt",
}

export interface CustomModel {
  id: string | null;
  name: string | null; // Keeping name for now, but making it nullable
  serviceUrl: string | null; // Renamed from url and made nullable
  apiKey: string | null; // Made nullable
}

export interface Settings {
  openAiApiKey: string | null;
  openAiBaseURL: string | null;
  screenshotOneApiKey: string | null;
  isImageGenerationEnabled: boolean;
  editorTheme: EditorTheme;
  generatedCodeConfig: Stack;
  codeGenerationModel: CodeGenerationModel;
  // Only relevant for hosted version
  isTermOfServiceAccepted: boolean;
  anthropicApiKey: string | null; // Added property for anthropic API key
  // Custom model configuration
  useCustomModel: boolean;
  customModel: CustomModel | null; // This will now use the updated CustomModel interface
}

export enum AppState {
  INITIAL = "INITIAL",
  CODING = "CODING",
  CODE_READY = "CODE_READY",
}

export enum ScreenRecorderState {
  INITIAL = "initial",
  RECORDING = "recording",
  FINISHED = "finished",
}

export interface CodeGenerationParams {
  generationType: "create" | "update";
  inputMode: "image" | "video" | "text";
  image: string;
  history?: string[];
  isImportedFromCode?: boolean;
}

export type FullGenerationSettings = CodeGenerationParams & Settings & {
  // Optional top-level properties for when useCustomModel is true
  customModelId?: string | null;
  customModelServiceUrl?: string | null;
  customModelApiKey?: string | null;
};
