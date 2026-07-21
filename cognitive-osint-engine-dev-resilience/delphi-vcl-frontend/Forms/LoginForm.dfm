object FrmLogin: TFrmLogin
  Left = 0
  Top = 0
  BorderStyle = bsSingle
  Caption = 'OSINT Giris'
  ClientHeight = 340
  ClientWidth = 460
  Color = clWhite
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -13
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poMainFormCenter
  TextHeight = 17
  object LblTitle: TLabel
    Left = 28
    Top = 24
    Width = 115
    Height = 33
    Caption = 'Hizli Giris'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = $00A0522D
    Font.Height = -24
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
  end
  object LblUsername: TLabel
    Left = 28
    Top = 86
    Width = 97
    Height = 17
    Caption = 'Kullanici adi'
    Font.Color = $00808080
  end
  object LblPassword: TLabel
    Left = 28
    Top = 156
    Width = 38
    Height = 17
    Caption = 'Sifre'
    Font.Color = $00808080
  end
  object LblStatus: TLabel
    Left = 28
    Top = 296
    Width = 46
    Height = 17
    Caption = 'Durum:'
    Font.Color = $00606060
  end
  object EdtUsername: TEdit
    Left = 28
    Top = 108
    Width = 404
    Height = 27
    BorderStyle = bsSingle
    Color = clWhite
    Font.Height = -12
    TabOrder = 0
  end
  object EdtPassword: TEdit
    Left = 28
    Top = 178
    Width = 404
    Height = 27
    BorderStyle = bsSingle
    Color = clWhite
    Font.Height = -12
    PasswordChar = '*'
    TabOrder = 1
  end
  object BtnLogin: TButton
    Left = 28
    Top = 232
    Width = 160
    Height = 36
    Caption = 'Giris Yap'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -12
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
    TabOrder = 2
    OnClick = BtnLoginClick
  end
  object BtnOpenRegister: TButton
    Left = 208
    Top = 232
    Width = 160
    Height = 36
    Caption = 'Yeni Kayit'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -12
    Font.Name = 'Segoe UI'
    Font.Style = []
    TabOrder = 3
    OnClick = BtnOpenRegisterClick
  end
end
