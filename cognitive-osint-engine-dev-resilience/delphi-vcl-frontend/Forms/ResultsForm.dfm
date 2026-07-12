object FrmResults: TFrmResults
  Left = 0
  Top = 0
  Caption = 'Sonuclar'
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
    Width = 84
    Height = 28
    Caption = 'Sonuclar'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -21
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
  end
  object LblAramaId: TLabel
    Left = 24
    Top = 64
    Width = 52
    Height = 15
    Caption = 'Arama ID'
  end
  object LblStatus: TLabel
    Left = 24
    Top = 536
    Width = 43
    Height = 15
    Caption = 'Durum:'
  end
  object EdtAramaId: TEdit
    Left = 24
    Top = 84
    Width = 180
    Height = 23
    TabOrder = 0
  end
  object BtnLoad: TButton
    Left = 216
    Top = 80
    Width = 120
    Height = 31
    Caption = 'Getir'
    TabOrder = 1
    OnClick = BtnLoadClick
  end
  object BtnClose: TButton
    Left = 344
    Top = 80
    Width = 120
    Height = 31
    Caption = 'Kapat'
    TabOrder = 2
    OnClick = BtnCloseClick
  end
  object MemoResults: TMemo
    Left = 24
    Top = 128
    Width = 732
    Height = 392
    ScrollBars = ssVertical
    TabOrder = 3
  end
end
