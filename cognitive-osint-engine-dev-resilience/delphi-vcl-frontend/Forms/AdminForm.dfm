object FrmAdmin: TAdminForm
  Left = 0
  Top = 0
  Caption = 'Admin Panel'
  ClientHeight = 680
  ClientWidth = 1120
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poMainFormCenter
  TextHeight = 15
  object LblTitle: TLabel
    Left = 12
    Top = 8
    Width = 111
    Height = 21
    Caption = 'Admin Paneli'
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -16
    Font.Name = 'Segoe UI'
    Font.Style = [fsBold]
    ParentFont = False
  end
  object PnlLeft: TPanel
    Left = 0
    Top = 36
    Width = 360
    Height = 644
    Align = alLeft
    BevelOuter = bvNone
    TabOrder = 0
    object LblUsers: TLabel
      Left = 12
      Top = 10
      Width = 76
      Height = 15
      Caption = 'Kullanicilar'
    end
    object GridUsers: TStringGrid
      Left = 12
      Top = 32
      Width = 336
      Height = 600
      ColCount = 4
      DefaultRowHeight = 22
      FixedCols = 0
      RowCount = 2
      TabOrder = 0
      ColWidths = (
        48
        130
        70
        80)
    end
  end
  object SplitterMain: TSplitter
    Left = 360
    Top = 36
    Width = 6
    Height = 644
    Align = alLeft
  end
  object PnlRight: TPanel
    Left = 366
    Top = 36
    Width = 754
    Height = 644
    Align = alClient
    BevelOuter = bvNone
    TabOrder = 1
    object PnlHistory: TPanel
      Left = 0
      Top = 0
      Width = 754
      Height = 300
      Align = alTop
      BevelOuter = bvNone
      TabOrder = 0
      object LblHistory: TLabel
        Left = 12
        Top = 10
        Width = 73
        Height = 15
        Caption = 'Arama Gecmisi'
      end
      object GridSearchHistory: TStringGrid
        Left = 12
        Top = 32
        Width = 730
        Height = 256
        ColCount = 5
        DefaultRowHeight = 22
        FixedCols = 0
        RowCount = 2
        TabOrder = 0
        ColWidths = (
          95
          240
          150
          95
          120)
      end
    end
    object SplitterRight: TSplitter
      Left = 0
      Top = 300
      Width = 754
      Height = 6
      Cursor = crVSplit
      Align = alTop
    end
    object PnlCompanies: TPanel
      Left = 0
      Top = 306
      Width = 754
      Height = 338
      Align = alClient
      BevelOuter = bvNone
      TabOrder = 1
      object LblCompanies: TLabel
        Left = 12
        Top = 10
        Width = 50
        Height = 15
        Caption = 'Sirketler'
      end
      object GridCompanies: TStringGrid
        Left = 12
        Top = 32
        Width = 730
        Height = 294
        ColCount = 10
        DefaultRowHeight = 22
        FixedCols = 0
        RowCount = 2
        TabOrder = 0
        ColWidths = (
          45
          130
          85
          75
          65
          120
          110
          95
          110
          120)
      end
    end
  end
end
