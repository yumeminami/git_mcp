"""Platform resolution utilities."""


def resolve_platform(ctx, platform):
    """Resolve platform name with smart fallback logic."""
    platform_name = platform or ctx.obj.platform

    # If platform_name is set but not configured, try to fall back to available platforms
    if platform_name:
        platform_config = ctx.obj.config.get_platform(platform_name)
        if not platform_config:
            available_platforms = ctx.obj.config.list_platforms()
            if len(available_platforms) == 1:
                platform_name = available_platforms[0]
                platform_config = ctx.obj.config.get_platform(platform_name)
            else:
                raise ValueError(
                    f"Platform '{platform_name}' not configured. Available: {available_platforms}"
                )
    else:
        available_platforms = ctx.obj.config.list_platforms()
        if len(available_platforms) == 1:
            platform_name = available_platforms[0]
            platform_config = ctx.obj.config.get_platform(platform_name)
        else:
            raise ValueError("Please specify --platform or set a default platform")

    if not platform_config:
        raise ValueError(f"Platform '{platform_name}' not configured")

    return platform_name, platform_config
