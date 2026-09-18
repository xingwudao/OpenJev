# OpenJev JavaScript SDK

Node.js 20+ ESM client, with TypeScript declarations and no runtime dependencies.
Import `sdk/js/index.js` locally; this package is not published.

```javascript
import { OpenJevClient, choice, noul } from "./sdk/js/index.js";

const client = new OpenJevClient();
const result = await client.systemOne({
  state: "The payment integration is failing.",
  questions: {
    team: choice("Who should handle this?", { billing: "Charges", technical: "Bugs" }),
    urgent: noul("This requires urgent action."),
  },
});
console.log(result.answers.team.choice);
```

`choice()`, `score()`, and `noul()` construct protocol questions. TypeScript
infers answer types and choice option keys from the request.
`OpenJevError` exposes HTTP `status` and protocol `code`.
Set `baseUrl` and `timeout` (milliseconds) on the client constructor.
