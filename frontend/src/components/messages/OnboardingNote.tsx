export function OnboardingNote() {
  return (
    <div className="flex flex-col space-y-4 bg-green-700 p-2 rounded text-stone-200 text-sm">
      <span>
        要使用截图转代码，{" "}
        <a
          className="inline underline hover:opacity-70"
          href="https://buy.stripe.com/8wM6sre70gBW1nqaEE"
          target="_blank"
        >
          购买一些积分（100次生成仅36美元）
        </a>{" "}
        或使用您自己具有GPT4 vision访问权限的OpenAI API密钥。{" "}
        <a
          href="https://github.com/abi/screenshot-to-code/blob/main/Troubleshooting.md"
          className="inline underline hover:opacity-70"
          target="_blank"
        >
          按照这些说明获取密钥。
        </a>{" "}
        然后将其粘贴到设置对话框中（上面的齿轮图标）。您的密钥仅保存在您的浏览器中，从不保存在我们的服务器上。
      </span>
    </div>
  );
}
