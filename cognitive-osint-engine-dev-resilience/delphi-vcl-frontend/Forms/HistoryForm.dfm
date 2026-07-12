object FrmHistory: TFrmHistory
  Left = 0
  Top = 0
  Caption = 'Arama Gecmisi'
  ClientHeight = 560
  ClientWidth = 780
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
    Width = 160
    Height = 28
    Caption = 'Arama Gecmisi'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -21
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
  end
  object LblStatus: TLabel
    Left = 24
    Top = 536
    Width = 43
    Height = 15
    Caption = 'Durum:'
  end
  object BtnLoad: TButton
    Left = 24
    Top = 64
    Width = 120
    Height = 31
    Caption = 'Getir'
    TabOrder = 0
    OnClick = BtnLoadClick
  end
  object BtnClose: TButton
    Left = 152
    Top = 64
    Width = 120
    Height = 31
    Caption = 'Kapat'
    TabOrder = 1
    OnClick = BtnCloseClick
  end
  object MemoHistory: TMemo
    Left = 24
    Top = 112
    Width = 732
    Height = 408
    ScrollBars = ssVertical
    TabOrder = 2
  end
end
