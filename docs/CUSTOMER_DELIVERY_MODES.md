# Customer Delivery Modes

The Project Factory supports three commercial delivery modes.

## 1. Transfer — Build & Give Me

Use when the customer wants the finished project as their own asset.

Factory flow:
1. Generate and validate the project.
2. Publish to a controlled delivery branch/repository.
3. Deploy to an explicitly selected destination.
4. Complete handoff/transfer of the repository, deployment project, domain configuration, and documentation as applicable.
5. Remove Factory operational access when the agreement requires it.

The Factory does not assume permanent ownership after handoff.

## 2. Managed — Build + Maintain

Use when the customer wants the Factory to operate the project.

Factory flow:
1. Generate and validate the project.
2. Keep the repository/deployment in the agreed managed environment.
3. Deliver the live URL and support contact.
4. Maintain the project under the agreed monthly/service scope.

Commercial model: build fee + recurring maintenance/service fee.

## 3. Decide Later — Build Now, Decide Later

Use when the customer has not yet decided whether to own or have the Factory maintain the project.

Factory flow:
1. Generate and validate the project.
2. Keep it in a controlled delivery environment.
3. Do not silently transfer ownership.
4. Record the later decision as either Transfer or Managed.

## Destination rules

- Never deploy a customer project into PromptStudio's production project.
- Never place customer credentials in source code or generated artifacts.
- Never assume the Factory owns a customer asset permanently.
- A customer-owned deployment must have an explicit destination and handoff plan.
- A managed deployment must have an explicit maintenance scope and access model.

## Cost rule

The Factory remains zero-cost-first. Paid hosting, providers, domains, or other services are introduced only when the customer or Factory revenue justifies them and the cost is explicit.
