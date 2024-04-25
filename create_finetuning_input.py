def create_new_context(task_description, non_punctuated, steinsaltz, punctuated):
    return (
    {"messages": [{"role": "system", "content": task_description},
                  {"role": "user", "content": f'Original Talmudic Passage:\n{non_punctuated}\n Commentary:\n{steinsaltz}'},
                  {"role": "assistant", "content": punctuated}]}
    )

if __name__ == '__main__':