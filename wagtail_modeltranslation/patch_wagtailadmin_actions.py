from wagtail.actions.create_alias import CreatePageAliasAction


class PatchedCreatePageAliasAction(CreatePageAliasAction):
    def __init__(
        self,
        page,
        *,
        recursive=False,
        parent=None,
        update_attrs=None, # Changed to support translated slugs
        update_locale=None,
        user=None,
        log_action="wagtail.create_alias",
        reset_translation_key=True,
        _mpnode_attrs=None,
    ):
        self.attrs = update_attrs

        super().__init__(
            page,
            recursive=recursive,
            parent=parent,
            update_slug="prova",
            update_locale=update_locale,
            user=user,
            log_action=log_action,
            reset_translation_key=reset_translation_key,
            _mpnode_attrs=_mpnode_attrs,
        )

    def _create_alias(
        self,
        page,
        *,
        recursive,
        parent,
        update_slug,
        update_locale,
        user,
        log_action,
        reset_translation_key,
        _mpnode_attrs,
    ):
        alias = super()._create_alias(
            page,
            recursive=recursive,
            parent=parent,
            update_slug=update_slug,
            update_locale=update_locale,
            user=user,
            log_action=log_action,
            reset_translation_key=reset_translation_key,
            _mpnode_attrs=_mpnode_attrs,
        )

        for attr in self.attrs:
            if "slug" in attr:
                setattr(alias, attr, self.attrs[attr])

        alias.save()
        return alias
