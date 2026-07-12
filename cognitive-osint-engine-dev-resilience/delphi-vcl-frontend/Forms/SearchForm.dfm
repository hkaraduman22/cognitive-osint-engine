object FrmSearch: TFrmSearch
  Left = 0
  Top = 0
  BorderStyle = bsDialog
  Caption = 'Arama Baslat'
  ClientHeight = 242
  ClientWidth = 520
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
    Top = 16
    Width = 89
    Height = 28
    Caption = 'Yeni Arama'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -21
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
  end
  object LblQuery: TLabel
    Left = 24
    Top = 72
    Width = 65
    Height = 15
    Caption = 'Arama metni'
  end
  object LblStatus: TLabel
    Left = 24
    Top = 200
    Width = 43
    Height = 15
    Caption = 'Durum:'
  end
  object EdtQuery: TEdit
    Left = 24
    Top = 92
    Width = 472
    Height = 23
    TabOrder = 0
  end
  object BtnPrepareSearch: TButton
    Left = 24
    Top = 144
    Width = 152
    Height = 32
    Caption = 'Aramayi Baslat'
    TabOrder = 1
    OnClick = BtnPrepareSearchClick
  end
  object BtnCancel: TButton
    Left = 176
    Top = 144
    Width = 120
    Height = 32
    Caption = 'Vazgec'
    TabOrder = 2
    OnClick = BtnCancelClick
  end
end
