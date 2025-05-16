import React from "react";
import { useAppStore } from "../../store/app-store";
import { AppState, Settings } from "../../types";
import OutputSettingsSection from "./OutputSettingsSection";
import { Stack } from "../../lib/stacks";
import { CodeGenerationModel, CODE_GENERATION_MODEL_DESCRIPTIONS } from "../../lib/models";
import { Select, SelectTrigger, SelectContent, SelectGroup, SelectItem } from "../ui/select";

interface GenerationSettingsProps {
  settings: Settings;
  setSettings: React.Dispatch<React.SetStateAction<Settings>>;
}

export const GenerationSettings: React.FC<GenerationSettingsProps> = ({
  settings,
  setSettings,
}) => {
  const { appState } = useAppStore();

  function setStack(stack: Stack) {
    setSettings((prev: Settings) => ({
      ...prev,
      generatedCodeConfig: stack,
    }));
  }

  const shouldDisableUpdates =
    appState === AppState.CODING || appState === AppState.CODE_READY;

  return (
    <div className="flex flex-col gap-y-2">
      <OutputSettingsSection
        stack={settings.generatedCodeConfig}
        setStack={setStack}
        shouldDisableUpdates={shouldDisableUpdates}
      />
      {/* 模型选择下拉框 */}
      <div className="flex flex-col gap-y-2">
        <div className="grid grid-cols-3 items-center gap-4">
          <span className="text-gray-500 text-sm">Select Model</span>
          <Select
            value={settings.codeGenerationModel}
            onValueChange={(value) =>
              setSettings((prev) => ({
                ...prev,
                codeGenerationModel: value as CodeGenerationModel,
              }))
            }
            disabled={shouldDisableUpdates}
          >
            <SelectTrigger className="col-span-2">
              {CODE_GENERATION_MODEL_DESCRIPTIONS[settings.codeGenerationModel]?.name || settings.codeGenerationModel}
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {Object.values(CodeGenerationModel).map((model) => (
                  <SelectItem key={model} value={model}>
                    {CODE_GENERATION_MODEL_DESCRIPTIONS[model]?.name || model}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
};
