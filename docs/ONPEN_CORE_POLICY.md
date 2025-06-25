# Valorium X — Open Core & Secret Sauce Policy

*This document is also available in French: [OPEN_CORE_POLICY.fr.md](OPEN_CORE_POLICY.fr.md)*

## What is Valorium X?

Valorium X is a next-generation cryptographic platform inspired by bio-blockchain concepts (Quadrit), designed for security, performance, and privacy.  
This repository contains the **open core**: all public logic, APIs, data structures, validation logic, and user/developer documentation.

## Open Core: What is public here

- Data structures (transactions, blocks, chain)
- APIs, public endpoints, CLI/GUI interfaces
- Basic validation logic (Quadrit hashing, integrity checks)
- Network wrappers, deployment scripts, testing tools
- User and developer documentation

## Secret Sauce: What is not here (and why)

This repository contains **none** of the critical elements ensuring the uniqueness, robustness, or advanced security of the system.  
The confidential part, not published, remains Valorium X’s internal know-how.

**Why?**  
Valorium X’s security relies on proven cryptographic principles and a rigorous architecture, but the exact “recipe” is strictly confidential, just like a trade secret.  
This protects innovation while allowing audit of open components.

## Audit & Trust

- Open bricks can be audited by the community, third parties, or partners under NDA.
- The confidential part may be subject to private audits or confidential certifications.

## Contributing

Contributions to the **open core** are welcome!  
For audit or restricted access, contact the Valorium X team at [contact@valoriumx.com](mailto:contact@valoriumx.com).

## License

The open core code is licensed under [MIT/Apache/AGPL] (please specify your choice).  
All confidential know-how remains the private property of Valorium X.

---

**NB:** Any reproduction or disclosure of the confidential part without authorization is strictly prohibited.