"""配置检查：仅验证本地字段，不联网、不打印密钥或服务地址。"""
from app.core.config import get_settings
from pydantic import ValidationError


def main() -> None:
    try:
        settings = get_settings()
    except ValidationError:
        raise SystemExit('缺少模型配置。请复制 .env.example 为 .env，填写 LLM_API_KEY、LLM_BASE_URL、LLM_MODEL。') from None
    if (settings.llm_api_key in {'your-api-key', 'test-only'}
            or '.example' in settings.llm_base_url
            or settings.llm_model == 'your-model-name'):
        raise SystemExit('模型配置仍为占位值，请填写供应商提供的真实配置。')
    if not settings.llm_base_url.startswith(('https://', 'http://')):
        raise SystemExit('LLM_BASE_URL 必须以 https:// 或 http:// 开头。')
    print('必填配置已填写；这不代表网络、额度或模型能力已验证。')


if __name__ == '__main__':
    main()
