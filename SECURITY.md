# Security policy

This repository is a public synthetic-data hackathon demo, not a production café service. Do not submit real customer data, café credentials, payment data, or unredacted screenshots in issues, discussions, or pull requests.

## Reporting a vulnerability

Please do not publish exploit details or suspected credentials in a public issue. Use GitHub's **Report a vulnerability** / private advisory flow for this repository if it is enabled. If that private channel is unavailable, contact the repository owner through their GitHub profile and share only the minimum reproduction details needed. Rotate any exposed credential immediately; deleting it from the current tree does not remove it from Git history.

## Supported scope

Reports about authentication/authorization, tenant or data isolation, unsafe action paths, secret exposure, injection, privacy leakage, or dependency compromise are in scope. Café menu facts, order state, seating, and staff actions in the public demo are synthetic. Google Maps directory data is live; report a product issue without treating a directory listing as a CaféMesh partner relationship.

The repository runs automated tests, a JavaScript dependency audit, a container build, and history-aware secret scanning in GitHub Actions. These checks reduce risk; they do not establish that the application is production secure.
