def task_filter(tasks_qs, filters: dict):
    if filters['search']:
        tasks_qs = tasks_qs.filter(title__icontains=filters['search'])

    if filters['priority']:
        tasks_qs = tasks_qs.filter(priority=filters['priority'])

    if filters['employee']:
        tasks_qs = tasks_qs.filter(employees=filters['employee'])

    if filters['tag']:
        tasks_qs = tasks_qs.filter(tags=filters['tag'])

    if filters['deadline']:
        tasks_qs = tasks_qs.filter(deadline=filters['deadline'])
    return tasks_qs

def project_filter(projects_qs, filters: dict):
    if filters['search']:
        projects_qs = projects_qs.filter(title__icontains=filters['search'])

    if filters['is_done']:
        projects_qs = projects_qs.filter(is_done=filters['is_done'])

    if filters['manager']:
        projects_qs = projects_qs.filter(manager=filters['manager'])

    if filters['task']:
        projects_qs = projects_qs.filter(tasks=filters['task'])

    if filters['deadline']:
        projects_qs = projects_qs.filter(deadline=filters['deadline'])
    return projects_qs
