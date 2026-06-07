---
type: stop
nummer: <% tp.system.prompt("Stoppnummer (1-12)") %>
periode: <% tp.system.suggester(["romeins-gallie","capetingen","renaissance-frankrijk","absolutisme","verlichting","franse-revolutie","napoleontisch-tijdperk"], ["romeins-gallie","capetingen","renaissance-frankrijk","absolutisme","verlichting","franse-revolutie","napoleontisch-tijdperk"]) %>
lat: <% tp.system.prompt("Breedtegraad") %>
long: <% tp.system.prompt("Lengtegraad") %>
tags: [stop]
---
# Stop <% tp.frontmatter.nummer %>: <% tp.file.title %>

**Locatie:**


## Zie ook

