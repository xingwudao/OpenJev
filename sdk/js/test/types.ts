import { OpenJevClient, choice, score, noul } from "../index.js";

const result = await new OpenJevClient().systemOne({
  state: { ticket: "Broken integration", attachments: [null, true, 3] },
  questions: {
    team: choice("Route", { billing: "Charges", technical: "Bugs" }),
    severity: score("Rate", ["Low", "High"]),
    urgent: noul("Urgent?"),
  },
});
const team: "billing" | "technical" = result.answers.team.choice;
const severity: number = result.answers.severity.score;
const urgent: number = result.answers.urgent.noul;
// @ts-expect-error A choice answer does not contain a score.
result.answers.team.score;
// @ts-expect-error Answer keys are inferred from the request.
result.answers.missing;
// @ts-expect-error Choice options are closed.
const unknown: "sales" = result.answers.team.choice;
void [team, severity, urgent, unknown];
