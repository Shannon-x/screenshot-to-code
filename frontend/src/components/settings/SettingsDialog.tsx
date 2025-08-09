import React from "react";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { FaCog } from "react-icons/fa";
import { EditorTheme, Settings } from "../../types";
import { Switch } from "../ui/switch";
import { Label } from "../ui/label";
import { Input } from "../ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger } from "../ui/select";
import { capitalize } from "../../lib/utils";
import { IS_RUNNING_ON_CLOUD } from "../../config";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../ui/accordion";
import { useLocale } from "../../hooks/useLocale";

interface Props {
  settings: Settings;
  setSettings: React.Dispatch<React.SetStateAction<Settings>>;
}

function SettingsDialog({ settings, setSettings }: Props) {
  const { t } = useLocale();
  
  const handleThemeChange = (theme: EditorTheme) => {
    setSettings((s) => ({
      ...s,
      editorTheme: theme,
    }));
  };

  return (
    <Dialog>
      <DialogTrigger>
        <FaCog />
      </DialogTrigger>
      <DialogContent className="flex flex-col">
        <DialogHeader className="flex-shrink-0">
          <DialogTitle>{t('settings.title')}</DialogTitle>
        </DialogHeader>

        <div className="overflow-y-auto flex-1 mt-4 pr-2" style={{ maxHeight: 'calc(90vh - 180px)' }}>
          <div className="flex items-center space-x-2">
          <Label htmlFor="image-generation">
            <div>{t('settings.enableImageGeneration')}</div>
            <div className="font-light mt-2 text-xs">
              使用DALL-E生成占位图片，更有趣但会增加成本
            </div>
          </Label>
          <Switch
            id="image-generation"
            checked={settings.isImageGenerationEnabled}
            onCheckedChange={() =>
              setSettings((s) => ({
                ...s,
                isImageGenerationEnabled: !s.isImageGenerationEnabled,
              }))
            }
          />
          </div>
          <div className="flex flex-col space-y-6">
          <div>
            <Label htmlFor="openai-api-key">
              <div>{t('settings.openAiApiKey')}</div>
              <div className="font-light mt-1 mb-2 text-xs leading-relaxed">
                仅保存在您的浏览器中，不会存储在服务器上。会覆盖您的 .env 配置
              </div>
            </Label>

            <Input
              id="openai-api-key"
              placeholder={t('settings.openAiApiKeyPlaceholder')}
              value={settings.openAiApiKey || ""}
              onChange={(e) =>
                setSettings((s) => ({
                  ...s,
                  openAiApiKey: e.target.value,
                }))
              }
            />
          </div>

          {!IS_RUNNING_ON_CLOUD && (
            <div>
              <Label htmlFor="openai-api-key">
                <div>{t('settings.openAiBaseUrl')}</div>
                <div className="font-light mt-2 leading-relaxed">
                  如果您不想使用默认地址，可以替换为代理URL
                </div>
              </Label>

              <Input
                id="openai-base-url"
                placeholder={t('settings.openAiBaseUrlPlaceholder')}
                value={settings.openAiBaseURL || ""}
                onChange={(e) =>
                  setSettings((s) => ({
                    ...s,
                    openAiBaseURL: e.target.value,
                  }))
                }
              />
            </div>
          )}

          <div>
            <Label htmlFor="anthropic-api-key">
              <div>{t('settings.anthropicApiKey')}</div>
              <div className="font-light mt-1 text-xs leading-relaxed">
                仅保存在您的浏览器中，不会存储在服务器上。会覆盖您的 .env 配置
              </div>
            </Label>

            <Input
              id="anthropic-api-key"
              placeholder={t('settings.anthropicApiKeyPlaceholder')}
              value={settings.anthropicApiKey || ""}
              onChange={(e) =>
                setSettings((s) => ({
                  ...s,
                  anthropicApiKey: e.target.value,
                }))
              }
            />
          </div>

          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="custom-model">
              <AccordionTrigger>{t('settings.customModelSettings')}</AccordionTrigger>
              <AccordionContent className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Label htmlFor="use-custom-model">
                    <div>{t('settings.useCustomModel')}</div>
                    <div className="font-light mt-2 text-xs">
                      使用您自己的AI模型API而不是内置模型
                    </div>
                  </Label>
                  <Switch
                    id="use-custom-model"
                    checked={settings.useCustomModel || false}
                    onCheckedChange={(checked) =>
                      setSettings((s) => ({
                        ...s,
                        useCustomModel: checked,
                        customModel: checked ? s.customModel || {
                          id: null,
                          name: null,
                          serviceUrl: null,
                          apiKey: null
                        } : null,
                      }))
                    }
                  />
                </div>

                {settings.useCustomModel && settings.customModel && (
                  <div className="space-y-4 p-4 border rounded-lg bg-gray-50 dark:bg-gray-800">
                    <div>
                      <Label htmlFor="custom-model-name">
                        <div>模型名称</div>
                        <div className="font-light mt-1 text-xs">
                          自定义模型的显示名称
                        </div>
                      </Label>
                      <Input
                        id="custom-model-name"
                        placeholder="例如：自定义 GPT-4"
                        value={settings.customModel.name || ""}
                        onChange={(e) =>
                          setSettings((s) => ({
                            ...s,
                            customModel: {
                              ...(s.customModel!),
                              name: e.target.value || null,
                            },
                          }))
                        }
                      />
                    </div>

                    <div>
                      <Label htmlFor="custom-model-id">
                        <div>{t('settings.customModelId')}</div>
                        <div className="font-light mt-1 text-xs">
                          要调用的模型标识符
                        </div>
                      </Label>
                      <Input
                        id="custom-model-id"
                        placeholder={t('settings.customModelIdPlaceholder')}
                        value={settings.customModel.id || ""}
                        onChange={(e) =>
                          setSettings((s) => ({
                            ...s,
                            customModel: {
                              ...(s.customModel!),
                              id: e.target.value || null,
                            },
                          }))
                        }
                      />
                    </div>

                    <div>
                      <Label htmlFor="custom-model-service-url">
                        <div>{t('settings.customModelServiceUrl')}</div>
                        <div className="font-light mt-1 text-xs">
                          模型服务的完整API端点地址
                        </div>
                      </Label>
                      <Input
                        id="custom-model-service-url"
                        placeholder={t('settings.customModelServiceUrlPlaceholder')}
                        value={settings.customModel.serviceUrl || ""}
                        onChange={(e) =>
                          setSettings((s) => ({
                            ...s,
                            customModel: {
                              ...(s.customModel!),
                              serviceUrl: e.target.value || null,
                            },
                          }))
                        }
                      />
                    </div>

                    <div>
                      <Label htmlFor="custom-model-api-key">
                        <div>{t('settings.customModelApiKey')}</div>
                        <div className="font-light mt-1 text-xs">
                          访问模型服务所需的API密钥
                        </div>
                      </Label>
                      <Input
                        id="custom-model-api-key"
                        type="password"
                        placeholder="输入API密钥"
                        value={settings.customModel.apiKey || ""}
                        onChange={(e) =>
                          setSettings((s) => ({
                            ...s,
                            customModel: {
                              ...(s.customModel!),
                              apiKey: e.target.value || null,
                            },
                          }))
                        }
                      />
                    </div>
                  </div>
                )}
              </AccordionContent>
            </AccordionItem>
          </Accordion>

          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="item-1">
              <AccordionTrigger>截图URL配置</AccordionTrigger>
              <AccordionContent>
                <Label htmlFor="screenshot-one-api-key">
                  <div className="leading-normal font-normal text-xs">
                    如果您想直接使用URL而不是自己截图，请添加ScreenshotOne API密钥。{" "}
                    <a
                      href="https://screenshotone.com?via=screenshot-to-code"
                      className="underline"
                      target="_blank"
                    >
                      免费获得100张截图/月
                    </a>
                  </div>
                </Label>

                <Input
                  id="screenshot-one-api-key"
                  className="mt-2"
                  placeholder={t('settings.screenshotOneApiKey')}
                  value={settings.screenshotOneApiKey || ""}
                  onChange={(e) =>
                    setSettings((s) => ({
                      ...s,
                      screenshotOneApiKey: e.target.value,
                    }))
                  }
                />
              </AccordionContent>
            </AccordionItem>
          </Accordion>

          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="item-1">
              <AccordionTrigger>主题设置</AccordionTrigger>
              <AccordionContent className="space-y-4 flex flex-col">
                <div className="flex items-center justify-between">
                  <Label htmlFor="app-theme">
                    <div>应用主题</div>
                  </Label>
                  <div>
                    <button
                      className="flex rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50t"
                      onClick={() => {
                        document
                          .querySelector("div.mt-2")
                          ?.classList.toggle("dark"); // enable dark mode for sidebar
                        document.body.classList.toggle("dark");
                        document
                          .querySelector('div[role="presentation"]')
                          ?.classList.toggle("dark"); // enable dark mode for upload container
                      }}
                    >
                      切换深色模式
                    </button>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <Label htmlFor="editor-theme">
                    <div>
                      代码编辑器主题 - 需要刷新页面才能更新
                    </div>
                  </Label>
                  <div>
                    <Select // Use the custom Select component here
                      name="editor-theme"
                      value={settings.editorTheme}
                      onValueChange={(value) =>
                        handleThemeChange(value as EditorTheme)
                      }
                    >
                      <SelectTrigger className="w-[180px]">
                        {capitalize(settings.editorTheme)}
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="cobalt">Cobalt</SelectItem>
                        <SelectItem value="espresso">Espresso</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
          </div>
        </div>

        <DialogFooter className="flex-shrink-0 mt-4 pt-4 border-t">
          <DialogClose>{t('common.save')}</DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default SettingsDialog;