def process_agent_request(agent, tenant, prompt):
    if tenant.monthly_tokens_used >= tenant.max_monthly_tokens:
        raise ("Token quota exceeded for this tenant.")

    run_response = agent.run(prompt)
    metrics = run_response.metrics
    tokens_used = metrics.get("total_tokens", 0)

    tenant.monthly_tokens_used += tokens_used
    tenant.save(update_fields=["monthly_tokens_used"])

    return run_response
