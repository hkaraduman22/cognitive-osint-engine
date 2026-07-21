object FrmRegister: TFrmRegister
  Left = 0
  Top = 0
  BorderStyle = bsSingle
  Caption = 'Yeni Kayit'
  ClientHeight = 360
  ClientWidth = 470
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
    Width = 146
    Height = 33
    Caption = 'Yeni Hesap'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = $00A0522D
    Font.Height = -24
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
  end
  object LblUsername: TLabel
    Left = 28
    Top = 84
    Width = 97
    Height = 17
    Caption = 'Kullanici adi'
    Font.Color = $00808080
  end
  object LblPassword: TLabel
    Left = 28
    Top = 150
    Width = 38
    Height = 17
    Caption = 'Sifre'
    Font.Color = $00808080
  end
  object LblPasswordAgain: TLabel
    Left = 28
    Top = 216
    Width = 105
    Height = 17
    Caption = 'Sifre (tekrar)'
    Font.Color = $00808080
  end
  object LblStatus: TLabel
    Left = 28
    Top = 316
    Width = 46
    Height = 17
    Caption = 'Durum:'
    Font.Color = $00606060
  end
  object EdtUsername: TEdit
    Left = 28
    Top = 106
    Width = 414
    Height = 27
    BorderStyle = bsSingle
    Color = clWhite
    Font.Height = -12
    TabOrder = 0
  end
  object EdtPassword: TEdit
    Left = 28
    Top = 172
    Width = 414
    Height = 27
    BorderStyle = bsSingle
    Color = clWhite
    Font.Height = -12
    PasswordChar = '*'
    TabOrder = 1
  end
  object EdtPasswordAgain: TEdit
    Left = 28
    Top = 238
    Width = 414
    Height = 27
    BorderStyle = bsSingle
    Color = clWhite
    Font.Height = -12
    PasswordChar = '*'
    TabOrder = 2
  end
  object BtnRegister: TButton
    Left = 28
    Top = 276
    Width = 140
    Height = 34
    Caption = 'Kayit Ol'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -12
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
    TabOrder = 3
    OnClick = BtnRegisterClick
  end
  object BtnCancel: TButton
    Left = 184
    Top = 276
    Width = 140
    Height = 34
    Caption = 'Vazgec'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -12
    Font.Name = 'Segoe UI'
    Font.Style = []
    TabOrder = 4
    OnClick = BtnCancelClick
  end
end
