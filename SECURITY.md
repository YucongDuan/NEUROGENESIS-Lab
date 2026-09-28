# Security and data boundary

This is a single-user local research workbench, not a hardened multi-tenant service. It binds to 127.0.0.1 only. Host and Origin are restricted; computation requests need a random process-session token and JSON content type. Requests are bounded at 750 kB, CSV at 500 kB and catalogue models impose numerical work bounds. Raw requests are not written into an access log.

The server does not authenticate multiple researchers, enforce institutional data policy, encrypt capsule files, support arbitrary code plugins or manage consent. Do not bind it to a public interface, use a tunnel to make it public, or input identifiable clinical records. Source_kind and licensing declarations are user-supplied; the program cannot establish their truth.

Inputs reject nonfinite values, unknown fields, duplicate JSON keys, unsupported paths and invalid model bounds. Capsules refuse symlinks and path escapes when reading individual artifacts, use a fixed inventory and do not overwrite existing destinations. CSV export prefixes formula-like string values to reduce spreadsheet formula interpretation; numeric negative values remain numeric. Reports escape injected HTML.

Integrity uses SHA-256 and ordered event digests, without signatures or trusted timestamps. Without an independently retained receipt digest, a writer can regenerate a coherent set of false records. Preserve independent anchors and use external signing/archival infrastructure when stronger custody is required. Those integrations are not implemented in this release.

Known deployment limits include denial-of-service by a local user, process termination during an output write, ordinary filesystem permission risks and platform-dependent numeric differences. Exclusive directory reservation does not guarantee atomic visibility during publication. A successful integrity check after completion is the accepted capsule state.

There is no device actuation, stimulation protocol, medical recommendation, personal risk score or consciousness classifier. Do not use numerical parameter changes as instructions for intervening in a person or animal.

Report security concerns privately to the project maintainer through a trusted channel established by the maintainer. No support email or response-time guarantee is invented by this package.
