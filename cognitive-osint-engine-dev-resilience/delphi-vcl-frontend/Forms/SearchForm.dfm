object FrmSearch: TFrmSearch
  Left = 0
  Top = 0
  BorderStyle = bsSingle
  Caption = 'Arama Baslat'
  ClientHeight = 260
  ClientWidth = 560
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
    Width = 118
    Height = 33
    Caption = 'Yeni Arama'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = $00A0522D
    Font.Height = -24
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
  end
  object LblQuery: TLabel
    Left = 28
    Top = 86
    Width = 82
    Height = 17
    Caption = 'Arama metni'
    Font.Color = $00808080
  end
  object LblStatus: TLabel
    Left = 28
    Top = 220
    Width = 46
    Height = 17
    Caption = 'Durum:'
    Font.Color = $00606060
  end
  object EdtQuery: TEdit
    Left = 28
    Top = 108
    Width = 504
    Height = 27
    BorderStyle = bsSingle
    Color = clWhite
    Font.Height = -12
    TabOrder = 0
  end
  object BtnPrepareSearch: TButton
    Left = 28
    Top = 164
    Width = 180
    Height = 36
    Caption = 'Aramayi Baslat'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWhite
    Font.Height = -12
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
    TabOrder = 1
    OnClick = BtnPrepareSearchClick
  end
  object BtnCancel: TButton
    Left = 224
    Top = 164
    Width = 140
    Height = 36
    Caption = 'Vazgec'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -12
    Font.Name = 'Segoe UI'
    Font.Style = []
    TabOrder = 2
    OnClick = BtnCancelClick
  end
end
