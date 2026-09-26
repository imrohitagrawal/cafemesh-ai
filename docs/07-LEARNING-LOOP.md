# Learning loops

**Customer:** feedback updates bounded preference weights for oat milk, sweetness, caramel, and quiet seating. Explicit preferences override inferred tendencies. UI shows signal and effect. Reset is available. Allergy and other safety rules never participate.

**Operations:** record predicted and actual preparation duration. Seeded history is marked separately from measured outcomes in `prep_observations`; seeded observations never calibrate estimates. A bounded moving average updates only after a configured minimum of measured samples; unreasonable durations are rejected.

**AI quality:** live provider failures and safety-guard events persist in the activity log and appear as unpromoted review signals in Operations. The dashboard never promotes them to trusted evaluation cases or changes prompts/policies. User-rejected-answer capture and an in-product promotion workflow remain a follow-up; any prompt/policy update still requires human review and regression verification. There is no automatic self-editing production loop.
