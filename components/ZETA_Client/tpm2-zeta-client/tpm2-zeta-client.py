import os
import hashlib
import argparse
import json
from tpm2_pytss import *
from tpm2_pytss.bindings import *

def create_signing_key_and_policy(tcti, app_name, program_path):
    """
    Erstellt einen Signaturschlüssel im TPM, der von allen Nutzern verwendet werden kann, und
    beschränkt die Nutzung dieses Schlüssels auf eine bestimmte Anwendung. Speichert auch den Hash 
    des Programms im TPM.

    Args:
        tcti (str): Der TCTI (Transmission Interface) Pfad zum TPM Gerät, z.B. "device:/dev/tpmrm0".
        app_name (str): Der Name der Anwendung, die den Schlüssel verwenden darf.
        program_path (str): Der Pfad zum Programm, dessen Hash im TPM gespeichert wird.

    Returns:
        None. Der Schlüssel und der Programm-Hash werden im TPM gespeichert, und die Metadaten 
        werden in einer JSON-Datei gespeichert.

    Output:
        Schreibt eine JSON-Datei mit den Schlüsseldaten und gibt Informationen über den
        erstellten Schlüssel und die Policy im Terminal aus.
    """
    # Berechne den Hash des Programms
    program_hash = hashlib.sha256()
    with open(program_path, 'rb') as f:
        while chunk := f.read(8192):
            program_hash.update(chunk)
    program_hash_digest = program_hash.digest()

    with ESAPI(tcti) as esapi:
        # Erzeuge die Policy, die den Zugriff auf den Schlüssel auf die angegebene Anwendung beschränkt
        policy_digest = esapi.hash(TPM2_ALG.SHA256, app_name.encode('utf-8')).digest

        # Erstelle den Primärschlüssel im TPM
        primary_template = TPMT_PUBLIC.parse({
            'type': 'RSA',
            'nameAlg': 'SHA256',
            'objectAttributes': (
                TPMA_OBJECT.SIGN_ENCRYPT |
                TPMA_OBJECT.USERWITHAUTH |
                TPMA_OBJECT.SENSITIVEDATAORIGIN |
                TPMA_OBJECT.RESTRICTED |
                TPMA_OBJECT.DECRYPT
            ),
            'authPolicy': policy_digest,
            'parameters': {
                'keyBits': 2048,
                'exponent': 0x10001,
                'scheme': {
                    'scheme': 'RSASSA',
                    'details': {'hashAlg': 'SHA256'},
                }
            },
            'unique': {'rsa': b''},
        })

        in_public = TPM2B_PUBLIC(primary_template)
        in_sensitive = TPM2B_SENSITIVE_CREATE()
        outside_info = TPM2B_DATA()
        creation_pcr = TPML_PCR_SELECTION()

        primary_handle, _, _, _, _ = esapi.CreatePrimary(
            ESYS_TR.RH_OWNER,
            in_sensitive,
            in_public,
            outside_info,
            creation_pcr
        )

        # Speichern des erstellten Schlüssels in einem persistenten Handle
        persistent_handle = 0x81010001
        esapi.EvictControl(
            ESYS_TR.RH_OWNER,
            primary_handle,
            persistent_handle
        )

        # Speichern des Programm-Hashes im TPM
        nv_index = 0x1500016  # Index für NV Speicher, kann angepasst werden
        nv_public = TPM2B_NV_PUBLIC(
            nvIndex=nv_index,
            nameAlg=TPM2_ALG.SHA256,
            attributes=(TPMA_NV.AUTHWRITE | TPMA_NV.AUTHREAD),
            dataSize=len(program_hash_digest)
        )

        esapi.NV_DefineSpace(
            ESYS_TR.RH_OWNER,
            b'',
            nv_public
        )

        esapi.NV_Write(
            ESYS_TR.RH_OWNER,
            nv_index,
            ESYS_TR.PASSWORD,
            program_hash_digest,
            0
        )

        # Speichern des Policy Digest, des Programm-Hashes und der Anwendung als Metadaten
        key_metadata = {
            'app_name': app_name,
            'policy_digest': policy_digest.hex(),
            'program_hash': program_hash_digest.hex(),
            'persistent_handle': persistent_handle,
            'nv_index': nv_index
        }
        with open(f'{app_name}_key_metadata.json', 'w') as f:
            json.dump(key_metadata, f, indent=4)

        print(f"Schlüssel für Anwendung '{app_name}' wurde erfolgreich erstellt und im TPM gespeichert.")
        print(f"Persistent Handle: {persistent_handle}")
        print(f"Policy Digest: {policy_digest.hex()}")
        print(f"Program Hash: {program_hash_digest.hex()} gespeichert im NV Index {nv_index}")

def verify_program_integrity(tcti, nv_index, program_path):
    """
    Verifiziert die Integrität des Programms, indem der zur Laufzeit berechnete Hash mit dem im TPM gespeicherten Hash verglichen wird.

    Args:
        tcti (str): Der TCTI (Transmission Interface) Pfad zum TPM Gerät, z.B. "device:/dev/tpmrm0".
        nv_index (int): Der NV Speicherindex, in dem der ursprüngliche Programm-Hash gespeichert ist.
        program_path (str): Der Pfad zum Programm, das verifiziert werden soll.

    Returns:
        bool: True, wenn der zur Laufzeit berechnete Hash mit dem im TPM gespeicherten Hash übereinstimmt, andernfalls False.
    """
    # Berechne den aktuellen Hash des Programms
    current_hash = hashlib.sha256()
    with open(program_path, 'rb') as f:
        while chunk := f.read(8192):
            current_hash.update(chunk)
    current_hash_digest = current_hash.digest()

    with ESAPI(tcti) as esapi:
        # Lese den gespeicherten Hash aus dem TPM NV Speicher
        nv_data = esapi.NV_Read(
            ESYS_TR.RH_OWNER,
            nv_index,
            ESYS_TR.PASSWORD,
            len(current_hash_digest),
            0
        )

    # Vergleiche die Hashes
    if nv_data == current_hash_digest:
        print("Programmintegrität verifiziert: Die Hashes stimmen überein.")
        return True
    else:
        print("Programmintegrität konnte nicht verifiziert werden: Die Hashes stimmen nicht überein.")
        return False

def main():
    """
    Hauptprogramm: Nimmt Parameter von der Kommandozeile und ermöglicht entweder die Erstellung eines Schlüssels und 
    eines Program-Hashes im TPM oder die Verifikation eines Programms zur Laufzeit.

    Parameter:
        --tcti (str): Der TCTI-Pfad zum TPM-Gerät, z.B. "device:/dev/tpmrm0".
        --app_name (str): Der Name der Anwendung, die den Schlüssel verwenden darf.
        --program_path (str): Der Pfad zum Programm, dessen Hash im TPM gespeichert wird.
        --verify (bool): Wenn gesetzt, wird das Programm zur Laufzeit verifiziert, anstatt einen neuen Schlüssel zu erstellen.

    Ausgabe:
        Eine JSON-Datei mit Schlüsseldaten und eine Ausgabe im Terminal, die den erfolgreichen
        Abschluss bestätigt oder das Ergebnis der Verifikation anzeigt.
    """
    parser = argparse.ArgumentParser(description="Erstellt einen Signaturschlüssel im TPM, speichert einen Programm-Hash, und ermöglicht die Verifikation der Programmintegrität zur Laufzeit.")
    parser.add_argument('--tcti', type=str, default="device:/dev/tpmrm0", help="Der TCTI-Pfad zum TPM-Gerät (z.B. device:/dev/tpmrm0).")
    parser.add_argument('--app_name', type=str, help="Der Name der Anwendung, die den Schlüssel verwenden darf.")
    parser.add_argument('--program_path', type=str, required=True, help="Der Pfad zum Programm, dessen Hash im TPM gespeichert wird.")
    parser.add_argument('--verify', action='store_true', help="Verifiziert das Programm zur Laufzeit.")

    args = parser.parse_args()

    if args.verify:
        with open(f'{args.app_name}_key_metadata.json', 'r') as f:
            metadata = json.load(f)
            nv_index = metadata['nv_index']
        verify_program_integrity(args.tcti, nv_index, args.program_path)
    else:
        if not args.app_name:
            print("Der Parameter --app_name ist erforderlich, wenn der Schlüssel erstellt wird.")
            return
        create_signing_key_and_policy(args.tcti, args.app_name, args.program_path)

if __name__ == "__main__":
    main()
