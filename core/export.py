import pandas as pd

def export_to_csv(fundings, filename='bitso_deposits.csv'):
    data = []
    for f in fundings:
        details = f.get('details', {})
        legal = f.get('legal_operation_entity', {})
        data.append({
            'Funding ID': f.get('fid'),
            'Status': f.get('status'),
            'Date': f.get('created_at'),
            'Amount': f.get('amount'),
            'Currency': f.get('currency'),
            'Asset': f.get('asset'),
            'Method': f.get('method'),
            'Method Name': f.get('method_name'),
            'Network': f.get('network'),
            'Protocol': f.get('protocol'),
            'Integration': f.get('integration'),
            'Sender Name': details.get('sender_name'),
            'Sender Ref': details.get('sender_ref'),
            'Sender CLABE': details.get('sender_clabe'),
            'Receive CLABE': details.get('receive_clabe'),
            'Sender Bank': details.get('sender_bank'),
            'CLAVE': details.get('clave'),
            'CLAVE Rastreo': details.get('clave_rastreo'),
            'Numeric Reference': details.get('numeric_reference'),
            'Concept': details.get('concepto'),
            'CEP Link': details.get('cep_link'),
            'Sender RFC/CURP': details.get('sender_rfc_curp'),
            'Deposit Type': details.get('deposit_type'),
            'Notes': details.get('notes'),
            'Emoji': details.get('emoji'),
            'Legal Entity Name': legal.get('name'),
            'Legal Country': legal.get('country_code_iso_2'),
            'Legal Image ID': legal.get('image_id')
        })

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Deposit summary saved to {filename}")