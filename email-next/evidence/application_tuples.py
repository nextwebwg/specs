"""Pure assertion2 tuple syntax/intersection; no signature or authority inference."""
RAW_OPERATIONS=frozenset({'answer','message','question','reaction','reaction-withdraw'})
OPERATIONS={'raw-event-v0':RAW_OPERATIONS,'mime-contribution-v0':RAW_OPERATIONS|{'attachment-message'}}
ORDERING=frozenset({'fixed-roster-v0','designated-member-v0'})

def validate_tuples(value,*,version='2'):
    allowed=dict(OPERATIONS)
    if version in ('4','5','6','7'):allowed={'mime-rich-v0':OPERATIONS['mime-contribution-v0']|{'rich-message'}}
    elif version=='3':allowed['mime-rich-v0']=OPERATIONS['mime-contribution-v0']|{'rich-message'}
    elif version!='2':raise ValueError('Tuple version')
    if version=='5':allowed['mime-rich-v0']=allowed['mime-rich-v0']|{'service-question','edit'}
    if not isinstance(value,list) or len(value)>2*len(allowed):raise ValueError('Application tuple inventory')
    previous=None
    for item in value:
        if not isinstance(item,dict) or set(item)!={'envelopeVersion','payload','ordering','operations'}:raise ValueError('Application tuple fields')
        if item['envelopeVersion']!=('3' if version in ('5','6','7') else '2' if version=='4' else '1') or not isinstance(item['payload'],str) or item['payload'] not in allowed or not isinstance(item['ordering'],str) or item['ordering'] not in ({'endpoint-quorum-v0'} if version in ('6','7') else ORDERING):raise ValueError('Application tuple key')
        key=(item['envelopeVersion'],item['payload'],item['ordering'])
        if previous is not None and key<=previous:raise ValueError('Duplicate or unordered application tuple')
        previous=key;ops=item['operations']
        if not isinstance(ops,list) or not ops or any(not isinstance(op,str) or op not in allowed[item['payload']] for op in ops) or ops!=sorted(set(ops)):raise ValueError('Application tuple operations')
    return value

def covers(tuples,application,ordering,*,version='2'):
    validate_tuples(tuples,version=version)
    if not isinstance(application,dict) or set(application)!={'envelopeVersion','payload','operations'}:raise ValueError('Selected application fields')
    selected=dict(application,ordering=ordering);validate_tuples([selected],version=version)
    return any(all(item[k]==selected[k] for k in ('envelopeVersion','payload','ordering')) and set(selected['operations'])<=set(item['operations']) for item in tuples)

def intersect(device_tuples,*,version='2'):
    """Caller must supply one independently verified set per exact device/key.

    Output is available syntax choices, not permission to select or send them.
    """
    if not isinstance(device_tuples,list) or not device_tuples:raise ValueError('Device evidence required')
    inventories=[{(t['envelopeVersion'],t['payload'],t['ordering']):set(t['operations']) for t in validate_tuples(items,version=version)} for items in device_tuples]
    common=set(inventories[0])
    for inventory in inventories[1:]:common.intersection_update(inventory)
    result=[]
    for key in sorted(common):
        operations=set.intersection(*(inventory[key] for inventory in inventories))
        if operations:result.append(dict(zip(('envelopeVersion','payload','ordering'),key),operations=sorted(operations)))
    return result
