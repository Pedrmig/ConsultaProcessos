import os
import subprocess
import sensiveis as pwd
import messagebox as msg
import unicodedata
import sys

# Código ANSI para iniciar negrito
start_bold = "\033[1m"
# Código ANSI para resetar a formatação
reset_bold = "\033[0m"


def executar_bcp(tabela, arquivo_txt):
    nome_arquivo, extensao = os.path.splitext(arquivo_txt)
    bcp = caminhobcp()
    if verifica_caminho(arquivo_txt) == 'Nome do arquivo':
        diretorio_projeto = os.path.dirname(os.path.abspath(__file__))
        nome_arquivo = os.path.join(diretorio_projeto, nome_arquivo)
        arquivo_txt = os.path.join(diretorio_projeto, arquivo_txt)

    comando = f'"{bcp}" {pwd.schema}."[{tabela}]" IN "{arquivo_txt}" -t "|" -C SQL_Latin1_General_CP1_CI_AS -c -S {pwd.endbanco} -U {pwd.usrbanco} -P {pwd.pwdbanco} -d {pwd.nomebanco} -e "{nome_arquivo}.err" -F 2 > "{nome_arquivo}.log"'
    print(comando)
    proc = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    stdout_text = decode_byte_to_text(stdout, 'ANSI')
    stderr_text = decode_byte_to_text(stderr, 'ANSI')

    if stdout is not None and stderr is not None:
        if 'Error' in stdout_text:
            msg.msgbox(
                f'Falha na carga do arquivo:\n {arquivo_txt} \nDescrição Erro:\n {decode_byte_to_text(stdout, "ANSI")}',
                msg.MB_OK, 'Erro BCP!')
            os.system('notepad ' + arquivo_txt)
            return None

        if stderr_text:
            print(decode_byte_to_text(stderr, "ANSI"))
            msg.msgbox(
                f'Falha na carga do arquivo:\n {arquivo_txt} \nDescrição Erro:\n {decode_byte_to_text(stderr, "ANSI")}',
                msg.MB_OK, 'Erro BCP!')
            os.system('notepad ' + arquivo_txt)
            return None

    num_rows_inserted = 0
    arquivolog = f"{nome_arquivo}.log"
    if os.path.exists(arquivolog):
        with open(arquivolog, 'r') as log:
            for line in log:
                if 'linhas copiadas' in line:
                    num_rows_inserted = int(line.split()[0])
                    break

    return num_rows_inserted


def caminhobcp():
    import shutil

    # Tenta encontrar o caminho do executável BCP no PATH
    bcp_path = shutil.which("bcp")
    return bcp_path


def decode_byte_to_text(entrada, decoder=''):
    import chardet

    if decoder == '':
        detected_encoding = chardet.detect(entrada)['encoding']
        if detected_encoding is not None:
            decoded_output = entrada.decode(detected_encoding)
        else:
            decoded_output = ''
    else:
        decoded_output = entrada.decode(decoder)
    return decoded_output


def verifica_caminho(string):
    nome_arquivo = os.path.basename(string)

    # Se a string for igual ao nome do arquivo, então é apenas o nome do arquivo
    if string == nome_arquivo:
        return "Nome do arquivo"
    else:
        return "Caminho completo"


def remover_caracteres_ilegais(texto):
    caracteres_permitidos = (
            ''.join(chr(i) for i in range(32, 126)) +
            ''.join(chr(i) for i in range(160, 255))
    )
    return ''.join(c for c in texto if c in caracteres_permitidos)


def para_ansi(texto):
    # Normalizar para a forma NFKD, depois codificar em ASCII ignorando erros
    texto_ascii = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore')
    # Decodificar de volta para string
    return texto_ascii.decode('ascii')


def formatar_data(data):
    if data.hour == 0 and data.minute == 0 and data.second == 0:
        return data.strftime('%Y/%m/%d')
    else:
        return data.strftime('%Y/%m/%d %H:%M:%S')


def caminhospadroes(caminho):
    """

    : param caminho: código dos caminhos padrões (dúvidas, confira lista abaixo).
    : return: retorna o caminho padrão selecionado (str)
    """
    import ctypes.wintypes

    # CSIDL	                        Decimal	Hex	    Shell	Description
    # CSIDL_ADMINTOOLS	            48	    0x30	5.0	    The file system directory that is used to store administrative tools for an individual user.
    # CSIDL_ALTSTARTUP	            29	    0x1D	 	    The file system directory that corresponds to the user's nonlocalized Startup program group.
    # CSIDL_APPDATA	                26	    0x1A	4.71	The file system directory that serves as a common repository for application-specific data.
    # CSIDL_BITBUCKET	            10	    0x0A	 	    The virtual folder containing the objects in the user's Recycle Bin.
    # CSIDL_CDBURN_AREA	            59	    0x3B	6.0	    The file system directory acting as a staging area for files waiting to be written to CD.
    # CSIDL_COMMON_ADMINTOOLS	    47	    0x2F	5.0	    The file system directory containing administrative tools for all users of the computer.
    # CSIDL_COMMON_ALTSTARTUP	    30	    0x1E	        NT-based only	The file system directory that corresponds to the nonlocalized Startup program group for all users.
    # CSIDL_COMMON_APPDATA	        35	    0x23	5.0	    The file system directory containing application data for all users.
    # CSIDL_COMMON_DESKTOPDIRECTORY	25	    0x19	        NT-based only	The file system directory that contains files and folders that appear on the desktop for all users.
    # CSIDL_COMMON_DOCUMENTS	    46	    0x2E	 	    The file system directory that contains documents that are common to all users.
    # CSIDL_COMMON_FAVORITES	    31	    0x1F	        NT-based only	The file system directory that serves as a common repository for favorite items common to all users.
    # CSIDL_COMMON_MUSIC	        53	    0x35	6.0	    The file system directory that serves as a repository for music files common to all users.
    # CSIDL_COMMON_PICTURES	        54	    0x36	6.0	    The file system directory that serves as a repository for image files common to all users.
    # CSIDL_COMMON_PROGRAMS	        23	    0x17	        NT-based only	The file system directory that contains the directories for the common program groups that appear on the Start menu for all users.
    # CSIDL_COMMON_STARTMENU	    22	    0x16	        NT-based only	The file system directory that contains the programs and folders that appear on the Start menu for all users.
    # CSIDL_COMMON_STARTUP	        24	    0x18	        NT-based only	The file system directory that contains the programs that appear in the Startup folder for all users.
    # CSIDL_COMMON_TEMPLATES	    45	    0x2D	        NT-based only	The file system directory that contains the templates that are available to all users.
    # CSIDL_COMMON_VIDEO	        55	    0x37	6.0	    The file system directory that serves as a repository for video files common to all users.
    # CSIDL_COMPUTERSNEARME	        61	    0x3D	6.0	    The folder representing other machines in your workgroup.
    # CSIDL_CONNECTIONS	            49	    0x31	6.0	    The virtual folder representing Network Connections, containing network and dial-up connections.
    # CSIDL_CONTROLS	            3	    0x03	 	    The virtual folder containing icons for the Control Panel applications.
    # CSIDL_COOKIES	                33	    0x21	 	    The file system directory that serves as a common repository for Internet cookies.
    # CSIDL_DESKTOP	                0	    0x00	 	    The virtual folder representing the Windows desktop, the root of the shell namespace.
    # CSIDL_DESKTOPDIRECTORY	    16	    0x10	 	    The file system directory used to physically store file objects on the desktop.
    # CSIDL_DRIVES	                17	    0x11	 	    The virtual folder representing My Computer, containing everything on the local computer: storage devices, printers, and Control Panel. The folder may also contain mapped network drives.
    # CSIDL_FAVORITES	            6	    0x06	 	    The file system directory that serves as a common repository for the user's favorite items.
    # CSIDL_FONTS	                20	    0x14	 	    A virtual folder containing fonts.
    # CSIDL_HISTORY	                34	    0x22	 	    The file system directory that serves as a common repository for Internet history items.
    # CSIDL_INTERNET	            1	    0x01	 	    A viritual folder for Internet Explorer.
    # CSIDL_INTERNET_CACHE	        32	    0x20	4.72	The file system directory that serves as a common repository for temporary Internet files.
    # CSIDL_LOCAL_APPDATA	        28	    0x1C	5.0	    The file system directory that serves as a data repository for local (nonroaming) applications.
    # CSIDL_MYDOCUMENTS	            5	    0x05	6.0	    The virtual folder representing the "My Documents" desktop item.
    # CSIDL_MYMUSIC	                13	    0x0D	6.0	    The file system directory that serves as a common repository for music files.
    # CSIDL_MYPICTURES	            39	    0x27	5.0	    The file system directory that serves as a common repository for image files.
    # CSIDL_MYVIDEO	                14	    0x0E	6.0	    The file system directory that serves as a common repository for video files.
    # CSIDL_NETHOOD	                19	    0x13	 	    A file system directory containing the link objects that may exist in the "My Network Places" virtual folder.
    # CSIDL_NETWORK	                18	    0x12	 	    A virtual folder representing Network Neighborhood, the root of the network namespace hierarchy.
    # CSIDL_PERSONAL	            5	    0x05	 	    The file system directory used to physically store a user's common repository of documents. (From shell version 6.0 onwards, CSIDL_PERSONAL is equivalent to CSIDL_MYDOCUMENTS, which is a virtual folder.)
    # CSIDL_PHOTOALBUMS	            69	    0x45	Vista	The virtual folder used to store photo albums.
    # CSIDL_PLAYLISTS	            63	    0x3F	Vista	The virtual folder used to store play albums.
    # CSIDL_PRINTERS	            4	    0x04	 	    The virtual folder containing installed printers.
    # CSIDL_PRINTHOOD	            27	    0x1B	 	    The file system directory that contains the link objects that can exist in the Printers virtual folder.
    # CSIDL_PROFILE	                40	    0x28	5.0	    The user's profile folder.
    # CSIDL_PROGRAM_FILES	        38	    0x26	5.0	    The Program Files folder.
    # CSIDL_PROGRAM_FILESX86	    42	    0x2A	5.0	    The Program Files folder for 32-bit programs on 64-bit systems.
    # CSIDL_PROGRAM_FILES_COMMON	43	    0x2B	5.0	    A folder for components that are shared across applications.
    # CSIDL_PROGRAM_FILES_COMMONX86	44	    0x2C	5.0	    A folder for 32-bit components that are shared across applications on 64-bit systems.
    # CSIDL_PROGRAMS	            2	    0x02	 	    The file system directory that contains the user's program groups (which are themselves file system directories).
    # CSIDL_RECENT	                8	    0x08	 	    The file system directory that contains shortcuts to the user's most recently used documents.
    # CSIDL_RESOURCES	            56	    0x38	6.0	    The file system directory that contains resource data.
    # CSIDL_RESOURCES_LOCALIZED	    57	    0x39	6.0	    The file system directory that contains localized resource data.
    # CSIDL_SAMPLE_MUSIC	        64	    0x40	Vista	The file system directory that contains sample music.
    # CSIDL_SAMPLE_PLAYLISTS	    65	    0x41	Vista	The file system directory that contains sample playlists.
    # CSIDL_SAMPLE_PICTURES	        66	    0x42	Vista	The file system directory that contains sample pictures.
    # CSIDL_SAMPLE_VIDEOS	        67	    0x43	Vista	The file system directory that contains sample videos.
    # CSIDL_SENDTO	                9	    0x09	 	    The file system directory that contains Send To menu items.
    # CSIDL_STARTMENU	            11	    0x0B	 	    The file system directory containing Start menu items.
    # CSIDL_STARTUP	                7	    0x07	 	    The file system directory that corresponds to the user's Startup program group.
    # CSIDL_SYSTEM	                37	    0x25	5.0	    The Windows System folder.
    # CSIDL_SYSTEMX86	            41	    0x29	5.0	    The Windows 32-bit System folder on 64-bit systems.
    # CSIDL_TEMPLATES	            21	    0x15	 	    The file system directory that serves as a common repository for document templates.
    # CSIDL_WINDOWS	                36	    0x24	5.0	    The Windows directory or SYSROOT.

    if caminho != 80:
        csidl_personal = caminho  # Caminho padrão
        shgfp_type_current = 0  # Para não pegar a pasta padrão e sim a definida como documentos

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.Shell32.SHGetFolderPathW(None, csidl_personal, None, shgfp_type_current, buf)

        return buf.value
    else:
        if os.name == 'nt':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        else:
            return os.path.join(os.path.expanduser('~'), 'downloads')


def caminhoselecionado(tipojanela=1, titulojanela='Selecione o caminho/arquivo:',
                       tipoarquivos=('Todos os Arquivos', '*.*'), caminhoini=caminhospadroes(5), arquivoinicial=''):
    """

    : param tipojanela: 1 — Seleciona Arquivo (Padrão); 2 — Seleciona caminho para salvar arquivo; 3 — Seleciona diretório.
    : param titulojanela: cabeçalho exibido na caixa de diálogo.
    : param tipoarquivos: extensão dos arquivos permitidos da seleção.
    : param caminhoini: caminho inicial.
    : param arquivoinicial: arquivo inicial.
    : return:
    """
    import tkinter as tk
    from tkinter import filedialog

    'Cria a janela raiz'
    root = tk.Tk()
    root.withdraw()

    if tipojanela == 1:
        retorno = filedialog.askopenfilename(title=titulojanela,
                                             initialdir=caminhoini, filetypes=tipoarquivos, initialfile=arquivoinicial)
        if retorno is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return None

    elif tipojanela == 2:
        name = filedialog.asksaveasfile(mode='w', defaultextension='.txt',
                                        filetypes=tipoarquivos,
                                        initialdir=caminhoini,
                                        title=titulojanela, initialfile=arquivoinicial)
        if name is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return None
        text2save = str(name.name)
        name.write('')
        retorno = text2save

    elif tipojanela == 3:
        name = filedialog.askdirectory(initialdir=caminhoini, title=titulojanela)
        if name is None:  # askdirectory return `None` if dialog closed with "cancel".
            return None
        text2save = name
        retorno = text2save

    else:
        return

    return retorno


def caminhoprojeto(subpasta=''):
    """
    : param subpasta: adiciona o caminho da subpasta dada como entrada (caso preenchido).
    : return: o caminho do projeto ao qual a rotina está inserida.
    """
    import errno

    try:
        caminho = ''
        if getattr(sys, 'frozen', False):
            caminho = os.path.dirname(sys.executable)
        else:
            caminho = os.path.dirname(os.path.abspath(__file__))

        if len(caminho) > 0:
            if len(subpasta) > 0:
                if not os.path.isdir(os.path.join(caminho, subpasta)):
                    os.mkdir(os.path.join(caminho, subpasta))
                caminho = os.path.join(caminho, subpasta)

        if os.path.isdir(caminho):
            return caminho
        else:
            return ''

    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass


def valores_nao_encontrados(df1, coluna1, df2=None, coluna2='', itemabuscar=''):
    """
    Retorna True se itemabuscar for encontrado na coluna1 do df1,
    ou os valores da coluna1 do df1 que não estão presentes na coluna2 do df2.
    A função garante que as colunas estejam no mesmo tipo para a comparação.

    Parâmetros:
    df1 (pandas.DataFrame): Primeiro DataFrame.
    coluna1 (str): Nome da coluna no df1 para comparar.
    df2 (pandas.DataFrame): Segundo DataFrame (pode ser None).
    coluna2 (str): Nome da coluna no df2 para comparar.
    itemabuscar (str): Item a ser buscado na coluna1 se df2 for None.
    """
    # Converte a coluna1 para o mesmo tipo (string neste caso)
    # df1[coluna1] = df1[coluna1].astype(str)

    if df2 is not None:
        # Se df2 é fornecido, compara com a coluna2 de df2
        df2[coluna2] = df2[coluna2].astype(str)
        return df1[~df1[coluna1].isin(df2[coluna2])]
    else:
        # Se df2 é None, verifica se itemabuscar está em coluna1
        return itemabuscar in df1[coluna1].values


def remover_caracteres_ilegais(texto):
    caracteres_permitidos = (
            ''.join(chr(i) for i in range(32, 126)) +
            ''.join(chr(i) for i in range(160, 255))
    )
    return ''.join(c for c in texto if c in caracteres_permitidos)
