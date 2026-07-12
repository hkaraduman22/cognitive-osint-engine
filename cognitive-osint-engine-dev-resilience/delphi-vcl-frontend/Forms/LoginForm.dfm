object FrmLogin: TFrmLogin
  Left = 0
  Top = 0
  Caption = 'OSINT Giris'
  ClientHeight = 304
  ClientWidth = 420
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  TextHeight = 15
  object LblTitle: TLabel
    Left = 24
    Top = 20
    Width = 87
    Height = 28
    Caption = 'Hizli Giris'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -21
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
  end
  object LblUsername: TLabel
    Left = 24
    Top = 76
    Width = 72
    Height = 15
    Caption = 'Kullanici adi'
  end
  object LblPassword: TLabel
    Left = 24
    Top = 132
    Width = 28
    Height = 15
    Caption = 'Sifre'
  end
  object LblStatus: TLabel
    Left = 24
    Top = 264
    Width = 43
    Height = 15
    Caption = 'Durum:'
  end
  object EdtUsername: TEdit
    Left = 24
    Top = 96
    Width = 372
    Height = 23
    TabOrder = 0
  end
  object EdtPassword: TEdit
    Left = 24
    Top = 152
    Width = 372
    Height = 23
    PasswordChar = '*'
    TabOrder = 1
  end
  object BtnLogin: TButton
    Left = 24
    Top = 192
    Width = 120
    Height = 30
    Caption = 'Giris Yap'
    TabOrder = 2
    OnClick = BtnLoginClick
  end
  object BtnOpenRegister: TButton
    Left = 152
    Top = 192
    Width = 120
    Height = 30
    Caption = 'Yeni Kayit'
    TabOrder = 3
    OnClick = BtnOpenRegisterClick
  end
end
