#!/usr/bin/env python3
"""
normalize.py - Normalizzazione risorse Kubernetes per confronto stabile

Questo modulo rimuove i campi dinamici e volatili dalle risorse Kubernetes
per permettere un confronto deterministico tra cluster diversi.

Campi rimossi:
- metadata.managedFields: gestito automaticamente da K8s
- metadata.creationTimestamp: varia tra deploy
- metadata.resourceVersion: interno K8s
- metadata.uid: univoco per risorsa
- metadata.selfLink: deprecato in K8s 1.20+
- metadata.generation: incrementa ad ogni modifica
- metadata.labels: rumore non necessario (opzionale con --show-metadata)
- metadata.annotations: spesso vuote o piene di metadata interne (opzionale con --show-metadata)
- status: stato runtime, non parte della configurazione desiderata
- spec.template.metadata: stessi campi per i pod template
- spec.jobTemplate.spec.template.metadata: stessi campi per i CronJob

Conversioni speciali:
- env arrays → dict: converte array di variabili d'ambiente in dizionario
  chiave=nome per evitare falsi positivi dovuti a riordinamenti

Uso: cat obj.json | python3 lib/normalize.py
Oppure: python3 lib/normalize.py < obj.json
"""
import sys
import json


def normalize(obj: dict, keep_metadata: bool = False) -> dict:
    """
    Normalizza un oggetto Kubernetes rimuovendo campi volatili.
    
    Args:
        obj: Dizionario rappresentante una risorsa Kubernetes
        keep_metadata: Se False (default), rimuove labels e annotations vuote
                      Se True, preserva labels e annotations (eccetto last-applied)
    
    Returns:
        Dizionario normalizzato pronto per il confronto
    
    Comportamento:
        - Rimuove sempre i campi dinamici (uid, resourceVersion, etc)
        - Rimuove sempre lo status (stato runtime)
        - Se keep_metadata=False: rimuove labels e annotations per ridurre rumore
        - Se keep_metadata=True: mantiene labels e annotations (utile per debug)
        - Converte sempre env arrays in dict per confronto non-posizionale
    """
    m = obj.get('metadata', {})
    
    # Rimozione campi dinamici (sempre rimossi)
    if 'managedFields' in m:
        m.pop('managedFields', None)
    for k in ('creationTimestamp', 'resourceVersion', 'uid', 'selfLink', 'generation'):
        m.pop(k, None)

    # Labels: rimuovi se non richiesto esplicitamente
    if not keep_metadata:
        m.pop('labels', None)

    # Annotations: rimuovi se non richiesto esplicitamente
    if not keep_metadata:
        m.pop('annotations', None)
    else:
        try:
            if 'annotations' in m and isinstance(m['annotations'], dict):
                m['annotations'].pop('kubectl.kubernetes.io/last-applied-configuration', None)
                if not m['annotations']:
                    m.pop('annotations', None)
        except Exception:
            pass

    # spec.template.metadata: rimuovi annotations e labels
    if not keep_metadata:
        try:
            if 'spec' in obj and 'template' in obj['spec']:
                tm = obj['spec']['template'].get('metadata', {})
                tm.pop('annotations', None)
                tm.pop('labels', None)
                if tm:
                    obj['spec']['template']['metadata'] = tm
                elif 'metadata' in obj['spec']['template']:
                    obj['spec']['template'].pop('metadata', None)
        except Exception:
            pass

    # spec.jobTemplate.spec.template.metadata per CronJob
    if not keep_metadata:
        try:
            if 'spec' in obj and 'jobTemplate' in obj['spec']:
                if 'spec' in obj['spec']['jobTemplate'] and 'template' in obj['spec']['jobTemplate']['spec']:
                    tm = obj['spec']['jobTemplate']['spec']['template'].get('metadata', {})
                    tm.pop('annotations', None)
                    tm.pop('labels', None)
                    if tm:
                        obj['spec']['jobTemplate']['spec']['template']['metadata'] = tm
                    elif 'metadata' in obj['spec']['jobTemplate']['spec']['template']:
                        obj['spec']['jobTemplate']['spec']['template'].pop('metadata', None)
        except Exception:
            pass

    # Converti env arrays in dizionari chiave=nome
    try:
        if 'spec' in obj and 'template' in obj['spec']:
            template_spec = obj['spec']['template'].get('spec', {})
            for container in template_spec.get('containers', []):
                if 'env' in container and isinstance(container['env'], list):
                    env_dict = {}
                    for env_var in container['env']:
                        if 'name' in env_var:
                            env_copy = {k: v for k, v in env_var.items() if k != 'name'}
                            env_dict[env_var['name']] = env_copy
                    container['env'] = env_dict
            for container in template_spec.get('initContainers', []):
                if 'env' in container and isinstance(container['env'], list):
                    env_dict = {}
                    for env_var in container['env']:
                        if 'name' in env_var:
                            env_copy = {k: v for k, v in env_var.items() if k != 'name'}
                            env_dict[env_var['name']] = env_copy
                    container['env'] = env_dict
    except Exception:
        pass

    # Converti env arrays per CronJob
    try:
        if 'spec' in obj and 'jobTemplate' in obj['spec']:
            if 'spec' in obj['spec']['jobTemplate'] and 'template' in obj['spec']['jobTemplate']['spec']:
                template_spec = obj['spec']['jobTemplate']['spec']['template'].get('spec', {})
                for container in template_spec.get('containers', []):
                    if 'env' in container and isinstance(container['env'], list):
                        env_dict = {}
                        for env_var in container['env']:
                            if 'name' in env_var:
                                env_copy = {k: v for k, v in env_var.items() if k != 'name'}
                                env_dict[env_var['name']] = env_copy
                        container['env'] = env_dict
                for container in template_spec.get('initContainers', []):
                    if 'env' in container and isinstance(container['env'], list):
                        env_dict = {}
                        for env_var in container['env']:
                            if 'name' in env_var:
                                env_copy = {k: v for k, v in env_var.items() if k != 'name'}
                                env_dict[env_var['name']] = env_copy
                        container['env'] = env_dict
    except Exception:
        pass

    # Rimuovi status
    obj.pop('status', None)
    obj['metadata'] = m
    return obj


def main():
    """Entry point per uso da command-line."""
    import argparse
    parser = argparse.ArgumentParser(description='Normalizza risorse Kubernetes')
    parser.add_argument('--show-metadata', action='store_true',
                       help='Mantieni labels e annotations')
    args = parser.parse_args()

    raw = sys.stdin.read()
    obj = json.loads(raw)
    normalized = normalize(obj, keep_metadata=args.show_metadata)
    print(json.dumps(normalized, sort_keys=True, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
