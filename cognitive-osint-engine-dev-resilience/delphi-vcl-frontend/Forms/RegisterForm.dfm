object FrmRegister: TFrmRegister
  Left = 0
  Top = 0
  BorderStyle = bsDialog
  Caption = 'Yeni Kayit'
  ClientHeight = 336
  ClientWidth = 420
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poMainFormCenter
  TextHeight = 15
  object LblTitle: TLabel
    Left = 24
    Top = 20
    Width = 117
    Height = 28
    Caption = 'Yeni Hesap'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -21
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
  end
  object LblUsername: TLabel
    Left = 24
    Top = 72
    Width = 72
    Height = 15
    Caption = 'Kullanici adi'
  end
  object LblPassword: TLabel
    Left = 24
    Top = 128
    Width = 28
    Height = 15
    Caption = 'Sifre'
  end
  object LblPasswordAgain: TLabel
    Left = 24
    Top = 184
    Width = 84
    Height = 15
    Caption = 'Sifre (tekrar)'
  end
  object LblStatus: TLabel
    Left = 24
    Top = 296
    Width = 43
    Height = 15
    Caption = 'Durum:'
  end
  object EdtUsername: TEdit
    Left = 24
    Top = 92
    Width = 372
    Height = 23
    TabOrder = 0
  end
  object EdtPassword: TEdit
    Left = 24
    Top = 148
    Width = 372
    Height = 23
    PasswordChar = '*'
    TabOrder = 1
  end
  object EdtPasswordAgain: TEdit
    Left = 24
    Top = 204
    Width = 372
    Height = 23
    PasswordChar = '*'
    TabOrder = 2
  end
  object BtnRegister: TButton
    Left = 24
    Top = 248
    Width = 120
    Height = 32
    Caption = 'Kayit Ol'
    TabOrder = 3
    OnClick = BtnRegisterClick
  end
  object BtnCancel: TButton
    Left = 152
    Top = 248
    Width = 120
    Height = 32
    Caption = 'Vazgec'
    TabOrder = 4
    OnClick = BtnCancelClick
  end
end
