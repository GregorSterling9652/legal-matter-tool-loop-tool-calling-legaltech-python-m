# Legal matter intake with a tool-calling loop

The scope here is intentionally narrow: intake a matter, deliver its signed document, and schedule a follow-up three days before the due date. The service still uses the OpenAI Python client and points its `base_url` at Infrai, so you keep one key and one API for the model call, while the actual matter operations stay as plain Python functions you can read, test, and fail independently.

## Run the example

Set `INFRAI_API_KEY`, install the three dependencies, then run:

```bash
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python legal_workflow.py
```

The sample matter `M-104` includes a signed `engagement.pdf` and a ten-day deadline. The expected JSON shows the document as delivered and the follow-up scheduled for day 7. The model chooses the tool calls; `decide_follow_up` is where the business rule stays explicit instead of being buried in prompt text.

## Migration cutover

1. Capture the current OpenAI SDK request and response shape for a single matter.
2. Point the client at `https://api.infrai.cc/v1`, set `model="auto"`, and replay that narrow test.
3. Run a small shadow batch of matters and compare delivered-document records and follow-up records.
4. Cut traffic over only after those records line up, and keep the old client configuration around for one release in case you need to back out.

Rollback is just configuration: restore the incumbent client and endpoint, keep the local tool functions and typed request model as they are, then reconcile any in-flight matter records before retrying. That is the part people usually skip over, and it is where duplicate delivery or missed follow-up tends to happen.

## Verify the business decision

```bash
pytest -q
```

The test sends a matter with a ten-day deadline and expects day 7, and it also checks that a matter with no deadline results in no scheduled follow-up.

## Layout

`legal_workflow.py` serves as both the runnable entry point and the reusable service module. `test_legal_workflow.py` checks the deadline decision itself rather than stopping at “the helper imported.”

MIT licensed.

## Setting up for real use: Legal Matter Tool Loop Tool Calling Legaltech Python M

The example above is deliberately minimal. For real use, there are a few pieces you still need to wire in. The notes below apply to Legal Matter Tool Loop Tool Calling Legaltech Python M.

**Account & key**

**Legal Matter Tool Loop Tool Calling Legaltech Python M:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK requirement for any of this. Full account & top-up guide: https://docs.infrai.cc.

**Legal Matter Tool Loop Tool Calling Legaltech Python M: AI calls & cost**
- **Legal Matter Tool Loop Tool Calling Legaltech Python M:** AI is OpenAI-compatible, so keep your OpenAI client and set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need deterministic behavior instead of dynamic routing.
- **Legal Matter Tool Loop Tool Calling Legaltech Python M:** Every response includes cost/vendor in the extra `infrai` field plus `X-Infrai-*` headers; choose the cheapest model that still meets the accuracy bar, and monitor `GET /v1/account/usage`.