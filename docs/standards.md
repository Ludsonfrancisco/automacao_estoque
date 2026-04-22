# Project Standards

All development in the **Totvs Sync Agent** project must follow these guidelines to ensure consistency and maintainability.

## Coding Style
- **Python Version**: 3.12+
- **Style Guide**: Follow [PEP 08](https://peps.python.org/pep-0008/).
- **Strings**: Use **single quotes** (`'`) unless double quotes are required to avoid escaping.
- **Asynchronous Code**: Use `async`/`await` for all Playwright interactions to ensure efficient resource usage.

## Language Conventions
- **Code & Docs**: All technical documentation, variables, function names, and comments must be in **English**.
- **UI References**: Any reference to Totvs Web interface elements (buttons, menus, labels) must be kept in **Portuguese (PT-BR)** as they appear in the system.

## Best Practices
- **Security**: Never hardcode credentials. Use `.env` files and `python-dotenv`.
- **Selectors**: Use robust Playwright selectors. Prefer `id` or `data-testid` when available.
- **Error Handling**: Implement retries for UI interactions and log failures clearly.
