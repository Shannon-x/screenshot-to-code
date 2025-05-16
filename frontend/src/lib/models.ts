// Keep in sync with backend (llm.py)
// Order here matches dropdown order
export enum CodeGenerationModel {
  // OpenAI models
  GPT_4_VISION = "gpt-4-vision-preview",
  GPT_4_TURBO_2024_04_09 = "gpt-4-turbo-2024-04-09",
  GPT_4O_2024_05_13 = "gpt-4o-2024-05-13",
  GPT_4O_2024_08_06 = "gpt-4o-2024-08-06",
  GPT_4O_2024_11_20 = "gpt-4o-2024-11-20",
  GPT_4_1_2025_04_14 = "gpt-4.1-2025-04-14",
  GPT_4_5_PREVIEW_2025_02_27 = "gpt-4.5-preview-2025-02-27",
  O4_MINI = "o4-mini",
  O1_PREVIEW_2024_09_12 = "o1-preview-2024-09-12",
  O1_2024_12_17 = "o1-2024-12-17",
  O3_2025_04_16 = "o3-2025-04-16",
  // Anthropic models
  CLAUDE_3_SONNET = "claude-3-sonnet-20240229",
  CLAUDE_3_5_SONNET_2024_06_20 = "claude-3-5-sonnet-20240620",
  CLAUDE_3_5_SONNET_2024_10_22 = "claude-3-5-sonnet-20241022",
  CLAUDE_3_7_SONNET_2025_02_19 = "claude-3-7-sonnet-20250219",
  // Gemini (Google) models (optional)
  GEMINI_2_0_FLASH_EXP = "gemini-2.0-flash-exp",
  GEMINI_2_0_FLASH = "gemini-2.0-flash",
  GEMINI_2_0_PRO_EXP = "gemini-2.0-pro-exp-02-05",
}

// Will generate a static error if a model in the enum above is not in the descriptions
export const CODE_GENERATION_MODEL_DESCRIPTIONS: {
  [key in CodeGenerationModel]: { name: string; inBeta: boolean };
} = {
  // OpenAI models
  [CodeGenerationModel.GPT_4_VISION]: { name: "GPT-4 Vision (deprecated)", inBeta: false },
  [CodeGenerationModel.GPT_4_TURBO_2024_04_09]: { name: "GPT-4 Turbo (deprecated)", inBeta: false },
  [CodeGenerationModel.GPT_4O_2024_05_13]: { name: "GPT-4o 2024-05-13", inBeta: false },
  [CodeGenerationModel.GPT_4O_2024_08_06]: { name: "GPT-4o 2024-08-06", inBeta: false },
  [CodeGenerationModel.GPT_4O_2024_11_20]: { name: "GPT-4o 2024-11-20", inBeta: false },
  [CodeGenerationModel.GPT_4_1_2025_04_14]: { name: "GPT-4.1 2025-04-14", inBeta: true },
  [CodeGenerationModel.GPT_4_5_PREVIEW_2025_02_27]: { name: "GPT-4.5 Preview", inBeta: true },
  [CodeGenerationModel.O4_MINI]: { name: "O4 Mini", inBeta: true },
  [CodeGenerationModel.O1_PREVIEW_2024_09_12]: { name: "O1 Preview", inBeta: true },
  [CodeGenerationModel.O1_2024_12_17]: { name: "O1 2024-12-17", inBeta: false },
  [CodeGenerationModel.O3_2025_04_16]: { name: "O3 2025-04-16", inBeta: true },
  // Anthropic models
  [CodeGenerationModel.CLAUDE_3_SONNET]: { name: "Claude 3 Sonnet", inBeta: false },
  [CodeGenerationModel.CLAUDE_3_5_SONNET_2024_06_20]: { name: "Claude 3.5 Sonnet", inBeta: false },
  [CodeGenerationModel.CLAUDE_3_5_SONNET_2024_10_22]: { name: "Claude 3.5 Sonnet (v2)", inBeta: false },
  [CodeGenerationModel.CLAUDE_3_7_SONNET_2025_02_19]: { name: "Claude 3.7 Sonnet", inBeta: false },
  // Gemini (optional)
  [CodeGenerationModel.GEMINI_2_0_FLASH_EXP]: { name: "Gemini Flash Exp", inBeta: true },
  [CodeGenerationModel.GEMINI_2_0_FLASH]: { name: "Gemini Flash", inBeta: true },
  [CodeGenerationModel.GEMINI_2_0_PRO_EXP]: { name: "Gemini Pro Exp", inBeta: true },
};
